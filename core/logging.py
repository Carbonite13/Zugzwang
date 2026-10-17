"""
Structlog configuration for Zugzwang.

Call ``configure()`` once at application startup (before any loggers are
obtained) to wire up the shared processor chain.  After that, every module
should obtain its logger with::

    import structlog
    logger = structlog.get_logger(__name__)

In ``dev`` profile the output is human-readable coloured console output.
In ``prod`` profile the output is newline-delimited JSON suitable for log
aggregation pipelines.
"""

from __future__ import annotations

import logging
import sys
from typing import Any

import structlog

__all__ = ["configure"]


def _safe_add_logger_name(
    logger: Any, method_name: str, event_dict: structlog.types.EventDict
) -> structlog.types.EventDict:
    """
    Safe replacement for ``structlog.stdlib.add_logger_name``.

    ``ProcessorFormatter`` routes foreign stdlib records through the pre-chain
    before the logger is fully resolved (e.g. during multiprocessing subprocess
    spawn), which means ``logger`` can be ``None``.  This wrapper guards
    against that case instead of raising ``AttributeError``.
    """
    if logger is not None:
        event_dict.setdefault("logger", getattr(logger, "name", str(logger)))
    return event_dict


def configure(profile: str = "dev") -> None:
    """
    Wire up structlog with a shared processor chain.

    Parameters
    ----------
    profile:
        ``"dev"``  – coloured, human-readable console output.
        ``"prod"`` – JSON output suitable for log aggregators.
    """
    shared_processors: list[structlog.types.Processor] = [
        # Inject the log level name ("info", "error", …)
        structlog.stdlib.add_log_level,
        # Inject logger name – uses the safe wrapper that handles None loggers
        # which occur when stdlib records are processed during subprocess spawn.
        _safe_add_logger_name,
        # Timestamp in ISO-8601 / UTC
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        # Render exception info attached via exc_info=True
        structlog.processors.format_exc_info,
        # Stack-info rendering
        structlog.processors.StackInfoRenderer(),
    ]

    if profile == "dev":
        renderer: structlog.types.Processor = structlog.dev.ConsoleRenderer(colors=True)
    else:
        renderer = structlog.processors.JSONRenderer()

    structlog.configure(
        processors=[
            *shared_processors,
            # Prepare the event dict for the chosen renderer
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Also configure the stdlib root logger so that third-party libraries
    # (uvicorn, httpx, sqlalchemy …) route their records through structlog.
    formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            *shared_processors,
            renderer,
        ],
        foreign_pre_chain=shared_processors,
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    # Remove any existing handlers that stdlib may have added
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.DEBUG if profile == "dev" else logging.INFO)
