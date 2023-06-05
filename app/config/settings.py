from enum import Enum
from functools import lru_cache
from typing import Mapping, Any

from pydantic import BaseSettings, validator
from uvicorn.config import LOG_LEVELS


class Environment(Enum):
    localdev: str = "localdev"
    dev: str = "dev"
    prod: str = "prod"


class DatabaseSettings(BaseSettings):
    name: str = "fastapi_db"
    user: str = "postgres"
    password: str = "postgres"
    host: str = "localhost"
    port: int = 5432

    class Config:
        env_prefix = "POSTGRES_DB_"

    @property
    def url(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

    @property
    def async_url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class Settings(BaseSettings):
    environment: Environment = Environment.localdev
    service: str = "fast-api-docker-poetry"
    port: int = int("8009")
    host: str = "0.0.0.0"
    log_level: str = "debug"
    app_reload: bool = False
    db_retry_window_seconds: int = 60
    otel_service_name: str = None
    otel_exporter_otlp_endpoint: str = None

    ALLOWED_CORS_ORIGINS: set = [
        "localhost",
        "127.0.0.1",
        "host.docker.internal",
        "testserver",
    ]

    @property
    def code_branch(self) -> str:
        if self.environment == Environment.prod:
            return "main"
        else:
            return "dev"

    @validator("log_level")
    def valid_loglevel(cls, level: str) -> str:
        if level not in LOG_LEVELS.keys():
            raise ValueError(f"log_level must be one of {LOG_LEVELS.keys()}")
        return level

    @validator("db_retry_window_seconds")
    def init_db_retry_window_seconds(cls, v: int, values: Mapping[str, Any]) -> int:  # noqa
        if values["environment"] == Environment.localdev:
            return 1

    @property
    def is_local_dev(self) -> bool:
        return self.environment == Environment.localdev


@lru_cache(maxsize=1)
def get_settings():
    return Settings()


@lru_cache()
def get_database_settings() -> DatabaseSettings:
    return DatabaseSettings()
