"""
Application configuration.

Configuration is loaded from ``config/.env`` via pydantic-settings.  If any
required field is missing or a validator fails, the process logs the full
error with structlog and exits immediately with code 1 – there is no silent
fallback to a ``None`` config.
"""

import sys
import logging
from pathlib import Path
from typing import Annotated, Literal, Optional, Self

from pydantic import EmailStr, ValidationError, WrapSerializer, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from core.validations import SecureString

__all__ = ["Config", "config"]

_log = logging.getLogger(__name__)

class Config(BaseSettings):

    model_config = SettingsConfigDict(
        env_file="config/.env",
        env_file_encoding="utf-8",
        extra="ignore",
        # Treat empty-string env values as absent so Optional fields fall back
        # to their defaults instead of failing coercion.
        env_ignore_empty=True,
    )

    # Profile 
    PROFILE: Literal["dev", "prod"]

    # Path configuration 
    DATA_DIRECTORY: str
    LOG_DIRECTORY: str
    TEMPLATE_DIRECTORY: str
    # When True the server creates DATA_DIRECTORY and LOG_DIRECTORY on startup.
    CREATE_DIRECTORY: bool = True

    # Supabase 
    # Supabase handles all persistence.  No raw DB connector fields are needed.
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: Annotated[str, WrapSerializer(SecureString)]

    # Uvicorn / deployment 
    UVICORN_HOST: str
    UVICORN_PORT: int
    UVICORN_WORKERS: int = 4

    # Metadata 
    VERSION: str = "0.0.1 (beta)"
    APP_NAME: str = "Zugzwang"
    AUTHOR_EMAIL: str = "Carbonite13"
    AUTHOR_NAME: Optional[EmailStr] = None

    # Validators 

    @model_validator(mode="after")
    def ensure_directories(self) -> Self:
        """Create runtime directories when CREATE_DIRECTORY is True."""
        log_dir = Path(self.LOG_DIRECTORY)
        data_dir = Path(self.DATA_DIRECTORY)
        tmpl_dir = Path(self.TEMPLATE_DIRECTORY)

        if not tmpl_dir.exists():
            raise ValueError(
                f"TEMPLATE_DIRECTORY does not exist: {tmpl_dir}"
            )

        if self.CREATE_DIRECTORY:
            log_dir.mkdir(parents=True, exist_ok=True)
            data_dir.mkdir(parents=True, exist_ok=True)
        else:
            missing = [str(d) for d in (log_dir, data_dir) if not d.exists()]
            if missing:
                raise ValueError(
                    f"Required directories are missing and CREATE_DIRECTORY=False: "
                    f"{', '.join(missing)}"
                )

        return self

def _load_config() -> Config:
    """
    Instantiate Config, log any validation errors in full, and exit if
    the configuration is invalid.  The application must never start with a
    missing or partial configuration.
    """
    try:
        return Config()
    except ValidationError as exc:
        # Log the full pydantic error summary as a single message so that
        # the structlog formatter receives a simple string, not a raw dict,
        # which avoids the NoneType crash in the foreign-log pre-chain.
        _log.critical("Configuration validation failed – cannot start:\n%s", exc)
        sys.exit(1)
    except Exception as exc:  # pragma: no cover – unexpected errors
        _log.critical(
            "Unexpected error while loading configuration: %s",
            exc,
            exc_info=True,
        )
        sys.exit(1)


config: Config = _load_config()