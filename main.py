"""
Application factory and entry point.

Import order matters:
  1. core.logging  – configures structlog before any other module logs
  2. config        – loads and validates settings (exits on failure)
  3. everything else
"""

from __future__ import annotations

# ── 1. Configure structlog first, before any other imports log ─────────────
# We read PROFILE from the environment directly so we can configure logging
# before the full Config model is instantiated.
import os
from core.logging import configure as configure_logging


from config import Config, config  # noqa: E402 – must follow logging setup
import structlog  # noqa: E402
from pathlib import Path  # noqa: E402

from fastapi import FastAPI, Request  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402
from fastapi.templating import Jinja2Templates  # noqa: E402

from api.v1 import router as v1_router  # noqa: E402
from api.v1.routes.pages import router as pages_router  # noqa: E402

logger = structlog.get_logger(__name__)
configure_logging(profile=config.PROFILE)


def create_app(cfg: Config) -> FastAPI:
    logger.info(
        "creating_application",
        app=cfg.APP_NAME,
        version=cfg.VERSION,
        profile=cfg.PROFILE,
    )

    app = FastAPI(
        title=cfg.APP_NAME,
        version=cfg.VERSION,
        description=f"The official API for {cfg.APP_NAME}.",
        contact={
            "name": cfg.AUTHOR_NAME,
            "email": cfg.AUTHOR_EMAIL,
        },
        docs_url="/docs",
        debug=cfg.PROFILE == "dev",
    )

    # Static files
    static_dir = Path(cfg.TEMPLATE_DIRECTORY) / "static"
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    logger.debug("static_files_mounted", directory=str(static_dir))

    # Jinja2 templates
    templates = Jinja2Templates(directory=cfg.TEMPLATE_DIRECTORY)
    logger.debug("templates_loaded", directory=cfg.TEMPLATE_DIRECTORY)

    # Inject config into every request state so templates can access it
    @app.middleware("http")
    async def inject_template_globals(request: Request, call_next):
        request.state.config = cfg
        request.state.templates = templates
        return await call_next(request)

    # API routes (versioned JSON endpoints)
    app.include_router(v1_router)
    logger.debug("router_mounted", router="api/v1")

    # Page routes (HTML – excluded from OpenAPI schema, tagged "pages")
    app.include_router(pages_router)
    logger.debug("router_mounted", router="pages")

    logger.info("application_ready", routes=len(app.routes))
    return app


app = create_app(config)