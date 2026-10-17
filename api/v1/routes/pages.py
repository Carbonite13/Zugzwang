"""
Page routes – server-rendered HTML views.

All responses are ``text/html``.  These routes are tagged "pages" and
excluded from the OpenAPI schema so they don't pollute the JSON API docs.
"""

from __future__ import annotations

import structlog
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from config import config
from api.v1.deps import get_templates

__all__ = ["router"]

logger = structlog.get_logger(__name__)

router = APIRouter(tags=["pages"], include_in_schema=False)

@router.get("/", response_class=HTMLResponse, summary="Home page")
async def index(
    request: Request,
    templates: Jinja2Templates = Depends(get_templates),
) -> HTMLResponse:
    """Render the application home page."""
    return templates.TemplateResponse(
        request, "index.html", {"config": config}
    )


@router.get("/about", response_class=HTMLResponse, summary="About page")
async def about(
    request: Request,
    templates: Jinja2Templates = Depends(get_templates),
) -> HTMLResponse:
    """Render the about page."""
    return templates.TemplateResponse(
        request, "about.html", {"config": config}
    )

@router.get("/auth/login", response_class=HTMLResponse, summary="Login page")
async def login_page(
    request: Request,
    templates: Jinja2Templates = Depends(get_templates),
) -> HTMLResponse:
    """Render the login form."""
    return templates.TemplateResponse(
        request, "auth/login.html", {"config": config}
    )


@router.get("/auth/register", response_class=HTMLResponse, summary="Register page")
async def register_page(
    request: Request,
    templates: Jinja2Templates = Depends(get_templates),
) -> HTMLResponse:
    """Render the registration form."""
    return templates.TemplateResponse(
        request, "auth/register.html", {"config": config}
    )
