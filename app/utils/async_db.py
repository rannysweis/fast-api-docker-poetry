import logging
from functools import lru_cache
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import get_database_settings, get_settings, Settings
from app.utils.async_session_maker import AsyncSessionMaker

logger = logging.getLogger(__name__)
settings: Settings = get_settings()


def get_async_db() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency that provides a sqlalchemy session"""
    return _get_async_sessionmaker().cached_sessionmaker()


@lru_cache()
def _get_async_sessionmaker() -> AsyncSessionMaker:
    url = get_database_settings().async_url

    return AsyncSessionMaker(url)


def shutdown() -> None:
    logger.info("Shutting down database connections")

    _get_async_sessionmaker().cached_engine.dispose()

