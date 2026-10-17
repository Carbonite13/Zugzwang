from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator, ValidationError, EmailStr, WrapSerializer
from typing import Literal, Self, Optional, Annotated
from pathlib import Path
from sqlalchemy.engine import URL
from functools import lru_cache
import sys

from core.validations import SecureString

__all__ = ["config"]

class Config(BaseSettings):

    model_config = SettingsConfigDict(
        env_file="config/.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    PROFILE: Literal['dev','prod']

    # path configurations
    DATA_DIRECTORY: str
    LOG_DIRECTORY: str
    TEMPLATE_DIRECTORY: str
    CREATE_DIRECTORY: Optional[bool] = True

    # database configurations
    ENGINE: Literal["postgresql", "sqlite3"]
    DB_NAME: str
    DB_USER: Optional[str]
    DB_PASSWORD: Annotated[str, Field(...), WrapSerializer(SecureString)]
    DB_HOST: Optional[str]
    DB_PORT: Optional[int]
    DEBUG: Optional[bool] = False

    # deployment configurations
    UVICORN_HOST: str
    UVICORN_PORT: int
    UVICORN_WORKERS: int = 4

    # Metadata
    VERSION: str = "0.0.1 (beta)"
    APP_NAME: str = "Zugzwang"
    AUTHOR_EMAIL: str = "Carbonite13"
    AUTHOR_NAME: EmailStr
    
    @model_validator(mode="after")
    def path_configuration_validator(self) -> Self:
        # check if the given paths can be interpreted as file paths/directory paths
        # which are valid
        _log_directory = Path(self.LOG_DIRECTORY)
        _data_directory = Path(self.DATA_DIRECTORY)

        if self.CREATE_DIRECTORY:
            # create the directories
            _log_directory.mkdir(exist_ok=True)
            _data_directory.mkdir(exist_ok=True)

        else:
            # Raise error, as the create permission wasnt provided
            # and the required runtime direcotries are missing
            raise ValidationError("Error parsing directory configuration")
            sys.exit(1)
        return self

    @model_validator(mode="after")
    def db_configuration_validator(self) -> Self:
        required_fields = {
            "sqlite3": ["DB_NAME"],
            "postgresql": ["DB_NAME", "DB_PASSWORD", "DB_HOST", "DB_PORT", "DB_USER"]
        }
        
        fields = required_fields.get(self.ENGINE, None)
        if fields is None:
            raise ValueError(f"Invalid database engine provided: {self.ENGINE}")
        
        for field in fields:
            if self.get(field, None) is None:
                raise ValidationError(f"Undefined values for required parameters {required_fields} for {self.ENGINE}")
                sys.exit(1)
        return self

    @property
    def db_url(self) -> str:
        if self.ENGINE == "sqlite3":
            return URL.create(
                drivername="sqlite",
                database=f"{self.DATA_DIRECTORY}/{self.DB_NAME}"
            )
        elif self.ENGINE == "postgresql":
            return URL.create(
                drivername="postgresql+asyncpg",
                username=self.DB_USER,
                password=self.DB_PASSWORD,
                host=self.DB_HOST,
                port=self.DB_PORT,
                database=self.DB_NAME
            )
        else:
            raise ValueError(f"Invalid database engine provided: {self.ENGINE}")

try:
    config = Config()
except ValidationError as error:
    pass