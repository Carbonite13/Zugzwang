"""
User routes – current user profile.
"""

from __future__ import annotations

import structlog
from fastapi import APIRouter, Depends

from api.v1.middleware.auth import get_current_user
from models.user import User

__all__ = ["router"]

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/me",
    summary="Get the current authenticated user",
    response_model=User,
)
async def me(user: User = Depends(get_current_user)) -> User:
    """Return the profile of the currently authenticated user."""
    logger.info("user_fetched", user_id=str(user.id))
    return user
