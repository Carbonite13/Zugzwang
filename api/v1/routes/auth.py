"""
Auth routes – register and login via the internal-auth Supabase edge function.

Only user creation (register) and token retrieval (login) are handled here.
All cryptographic operations (hashing, JWT signing/verifying, refresh) are
delegated to the edge function or to the Supabase SDK (get_client()).
"""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from models.auth import (
    AuthError,
    AuthSuccess,
    LoginRequest,
    RegisterRequest,
)
from core.supabase import internal_auth

__all__ = ["router"]

router = APIRouter(tags=["auth"])

@router.post(
    "/register",
    summary="Register a new user",
    response_model=AuthSuccess,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"description": "Invalid body or registration failure"},
        403: {"description": "Registration disabled"},
        409: {"description": "Username already in use"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal error"},
    },
)
async def register(payload: RegisterRequest) -> JSONResponse:
    """
    Create a new user account via the internal-auth edge function.

    The edge function may return HTTP 201 together with an error body if
    account creation succeeded but the immediate sign-in failed (documented
    edge case).  We validate the body as ``AuthSuccess | AuthError`` and
    surface the error appropriately.
    """
    result = await internal_auth(payload)

    if isinstance(result, AuthError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.error,
        )

    return JSONResponse(
        content=result.model_dump(mode="json"),
        status_code=status.HTTP_201_CREATED,
    )

@router.post(
    "/login",
    summary="Authenticate and retrieve a session token",
    response_model=AuthSuccess,
    responses={
        401: {"description": "Invalid credentials"},
        403: {"description": "Login disabled"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal error"},
    },
)
async def login(payload: LoginRequest) -> JSONResponse:
    """
    Authenticate with identifier/username/email + password via the
    internal-auth edge function and return an ``AuthSuccess`` body containing
    the access token, refresh token, and expiry.
    """
    result = await internal_auth(payload)

    if isinstance(result, AuthError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result.error,
        )

    return JSONResponse(content=result.model_dump(mode="json"))
