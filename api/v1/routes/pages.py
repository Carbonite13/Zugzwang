"""
Index / home page route.
"""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from config import config
from api.v1.deps import get_templates

__all__ = ["router"]

router = APIRouter()

@router.get("/", response_class=HTMLResponse, summary="Home page")
async def index(
    request: Request,
    templates: Jinja2Templates = Depends(get_templates),
) -> HTMLResponse:
    """Render the application home page."""
    return templates.get_template("index.html").render(request=request, config=config)
