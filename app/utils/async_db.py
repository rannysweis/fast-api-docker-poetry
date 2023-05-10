import logging
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import get_database_settings, get_settings, Settings
from app.utils.async_session_maker import AsyncSessionMaker

logger = logging.getLogger(__name__)
settings: Settings = get_settings()


def get_async_db() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency that provides a sqlalchemy session"""
    async_url = get_database_settings().async_url
    return AsyncSessionMaker(async_url).cached_sessionmaker()


def shutdown() -> None:
    logger.info("Shutting down database connections")

    async_url = get_database_settings().async_url
    AsyncSessionMaker(async_url).cached_engine.dispose()
