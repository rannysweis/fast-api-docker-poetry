from contextlib import asynccontextmanager

from sqlalchemy import AsyncAdaptedQueuePool
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession

from app.config.settings import get_database_settings

async_url = get_database_settings().async_url
engine = create_async_engine(async_url,
                             pool_pre_ping=True,
                             poolclass=AsyncAdaptedQueuePool,
                             pool_size=1,
                             max_overflow=1)
sessionmaker = async_sessionmaker(bind=engine, expire_on_commit=False)


@asynccontextmanager
async def get_db_session() -> AsyncSession:
    session = sessionmaker()
    async with session.begin():
        yield session


async def shutdown() -> None:
    if engine is not None:
        await engine.dispose()
