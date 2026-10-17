"""
Authentication middleware / FastAPI dependency.

Provides ``get_current_user`` – a reusable dependency that:
  1. Extracts the Bearer token from the Authorization header.
  2. Calls supabase.auth.get_user(token) – the SDK handles all JWT
     verification, expiry checks, and key rotation.
  3. Maps the response onto the application-layer ``User`` model.

Usage
-----
    from api.v1.middleware.auth import get_current_user
    from models.user import User

    @router.get("/protected")
    async def protected(user: User = Depends(get_current_user)):
        ...
"""

from __future__ import annotations

import structlog
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from core.supabase import get_client
from models.user import User

__all__ = ["get_current_user"]

logger = structlog.get_logger(__name__)

# FastAPI security scheme – extracts "Bearer <token>" from the header
_bearer = HTTPBearer(auto_error=True)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> User:
    """
    Verify the Bearer JWT via the Supabase SDK and return the current user.

    Raises HTTP 401 if the token is missing, expired, or invalid.
    All cryptographic verification is handled by the SDK.
    """
    token = credentials.credentials
    client = await get_client()

    try:
        response = await client.auth.get_user(token)
    except Exception as exc:
        logger.warning("token_verification_failed", error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    if response is None or response.user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    sb_user = response.user
    # Extract username from user_metadata if the edge function stored it there.
    meta = sb_user.user_metadata or {}
    return User(
        id=sb_user.id,
        username=meta.get("username"),
        email=sb_user.email,
    )
