"""
Shared FastAPI dependencies for page routes.

``get_templates()`` is a request-scoped dependency that retrieves the
``Jinja2Templates`` instance injected into ``request.state`` by the
middleware in ``main.py``.  Page route handlers declare it as a parameter
so they stay decoupled from the application factory.
"""

from fastapi import Request
from fastapi.templating import Jinja2Templates

__all__ = ["get_templates"]

def get_templates(request: Request) -> Jinja2Templates:
    """Return the ``Jinja2Templates`` instance stored on request state."""
    return request.state.templates
