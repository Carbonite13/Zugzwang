"""
The active function is version 7. These models match its request body and current success allowlist: ok, user.id, user.username, session.access_token, session.refresh_token, and session.expires_at.
---
HTTP outcomes

Error bodies use {"error": "…"}. The function can return these statuses:

    400 — invalid body or input, unknown action, or registration failure
    401 — invalid login credentials
    403 — signup/login disabled or IP denied
    405 — unsupported method
    409 — username already in use
    413 — request too large
    429 — rate limit exceeded; also includes a Retry-After header
    500 — request processing failure

One current edge case: if account creation succeeds but the immediate sign-in fails, the function returns an error body with HTTP 201. Validate the body as AuthSuccess | AuthError rather than treating every 201 as a successful login.

---
Parse a request or response like this:

request = TypeAdapter(AuthRequest).validate_python(request_json)
response = auth_response_adapter.validate_python(response_json)
"""

from typing import Annotated, Literal, Union
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    TypeAdapter,
    field_validator,
    model_validator,
)

Password = Annotated[str, StringConstraints(min_length=1, max_length=1024)]
RegisterUsername = Annotated[
    str,
    StringConstraints(
        min_length=3,
        max_length=32,
        pattern=r"^[A-Za-z0-9_.-]{3,32}$",
    ),
]


class RequestModel(BaseModel):
    # The function ignores unknown request fields.
    model_config = ConfigDict(extra="ignore")


class RegisterRequest(RequestModel):
    action: Literal["register"]
    email: str = Field(min_length=1, max_length=320)
    username: RegisterUsername
    password: Password

    @field_validator("email", "username", mode="before")
    @classmethod
    def strip_registration_values(cls, value):
        return value.strip() if isinstance(value, str) else value

    @field_validator("email")
    @classmethod
    def email_must_contain_at(cls, value: str) -> str:
        # Matches the function's check; it does not perform full email validation.
        if "@" not in value:
            raise ValueError("email must contain '@'")
        return value


class LoginRequest(RequestModel):
    action: Literal["login"]
    password: Password
    identifier: str | None = Field(default=None, max_length=320)
    username: str | None = Field(default=None, max_length=320)
    email: str | None = Field(default=None, max_length=320)

    @field_validator("identifier", "username", "email", mode="before")
    @classmethod
    def strip_login_values(cls, value):
        return value.strip() if isinstance(value, str) else value

    @model_validator(mode="after")
    def require_login_identifier(self):
        # The function prioritizes identifier, then username, then email.
        selected = (
            self.identifier
            if self.identifier is not None
            else self.username
            if self.username is not None
            else self.email
        )
        if not selected:
            raise ValueError("provide identifier, username, or email")
        return self


AuthRequest = Annotated[
    Union[RegisterRequest, LoginRequest],
    Field(discriminator="action"),
]


class AuthUser(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: UUID
    username: str | None = None


class AuthSession(BaseModel):
    model_config = ConfigDict(extra="ignore")

    access_token: str
    refresh_token: str
    expires_at: int


class AuthSuccess(BaseModel):
    model_config = ConfigDict(extra="ignore")

    ok: Literal[True]
    user: AuthUser
    session: AuthSession


class AuthError(BaseModel):
    model_config = ConfigDict(extra="ignore")

    error: str


AuthResponse = Union[AuthSuccess, AuthError]
auth_response_adapter = TypeAdapter(AuthResponse)