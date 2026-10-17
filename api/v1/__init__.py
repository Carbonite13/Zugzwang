"""
API v1 router – aggregates all v1 sub-routers.
"""

from fastapi import APIRouter

from api.v1.routes.auth import router as auth_router
from api.v1.routes.pages import router as pages_router

router = APIRouter(prefix="/api/v1")
router.include_router(auth_router)
router.include_router(pages_router)