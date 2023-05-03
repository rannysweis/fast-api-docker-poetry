import logging
from functools import lru_cache
from typing import Iterator

import backoff
import psycopg2
from fastapi_restful.session import FastAPISessionMaker
from psycopg2 import OperationalError
from sqlalchemy.orm import Session

from app.config.settings import get_database_settings, get_settings, Settings

logger = logging.getLogger(__name__)
settings: Settings = get_settings()


def get_db() -> Iterator[Session]:
    """FastAPI dependency that provides a sqlalchemy session"""
    return _get_fastapi_sessionmaker().cached_sessionmaker()


@lru_cache()
def _get_fastapi_sessionmaker() -> FastAPISessionMaker:
    url = get_database_settings().url

    return FastAPISessionMaker(url)


def shutdown() -> None:
    logger.info("Shutting down database connections")

    _get_fastapi_sessionmaker().cached_engine.dispose()


@backoff.on_exception(backoff.expo, OperationalError, max_time=settings.db_retry_window_seconds, logger=logger)
def wait_for_postgres() -> None:
    print(f"Connecting to postgres...")
    dsn = get_database_settings().url
    conn = psycopg2.connect(dsn)
    cur = conn.cursor()
    cur.execute("SELECT 1;")
    cur.close()
    conn.close()
    print(f"Successfully connected to postgres...")
