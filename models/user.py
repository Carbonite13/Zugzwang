"""
User domain model.

Represents the application-layer view of a user, hydrated from the
Supabase auth.get_user() response.  Only the fields exposed by the
internal-auth edge function allowlist are captured here.
"""

from uuid import UUID
from pydantic import BaseModel, ConfigDict

__all__ = ["User"]

class User(BaseModel):
    """Authenticated user, as returned by Supabase auth.get_user()."""

    model_config = ConfigDict(extra="ignore")

    id: UUID
    username: str | None = None
    email: str | None = None
