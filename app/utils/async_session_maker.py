from contextlib import asynccontextmanager
from typing import Optional, AsyncIterator

from sqlalchemy import AsyncAdaptedQueuePool
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine, AsyncSession

"""
Used https://github.com/yuval9313/FastApi-RESTful/blob/master/fastapi_restful/session.py as example 
"""


class AsyncSessionMaker:
    """
    A convenience class for managing a (cached) sqlalchemy ORM engine and sessionmaker.

    Intended for use creating ORM sessions injected into endpoint functions by FastAPI.
    """

    def __init__(self, database_uri: str):
        """
        `database_uri` should be any sqlalchemy-compatible database URI.

        In particular, `sqlalchemy.create_engine(database_uri)` should work to create an engine.

        Typically, this would look like:

            "<scheme>://<user>:<password>@<host>:<port>/<database>"

        A concrete example looks like "postgresql://db_user:password@db:5432/app"
        """
        self.database_uri = database_uri

        self._cached_engine: Optional[AsyncEngine] = None
        self._cached_sessionmaker: Optional[async_sessionmaker] = None

    @property
    def cached_engine(self) -> AsyncEngine:
        """
        Returns a lazily-cached sqlalchemy engine for the instance's database_uri.
        """
        engine = self._cached_engine
        if engine is None:
            engine = self.get_new_engine()
            self._cached_engine = engine
        return engine

    @property
    def cached_sessionmaker(self) -> async_sessionmaker:
        """
        Returns a lazily-cached sqlalchemy sessionmaker using the instance's (lazily-cached) engine.
        """
        sessionmaker = self._cached_sessionmaker
        if sessionmaker is None:
            sessionmaker = self.get_new_sessionmaker(self.cached_engine)
            self._cached_sessionmaker = sessionmaker
        return sessionmaker

    def get_new_engine(self) -> AsyncEngine:
        """
        Returns a new sqlalchemy engine using the instance's database_uri.
        """
        return get_engine(self.database_uri)

    def get_new_sessionmaker(self, engine: Optional[AsyncEngine]) -> async_sessionmaker:
        """
        Returns a new sessionmaker for the provided sqlalchemy engine. If no engine is provided, the
        instance's (lazily-cached) engine is used.
        """
        engine = engine or self.cached_engine
        return get_sessionmaker_for_engine(engine)

    def get_db(self) -> AsyncIterator[AsyncSession]:
        """
        A generator function that yields a sqlalchemy orm session and cleans up the session once resumed after yielding.

        Can be used directly as a context-manager FastAPI dependency, or yielded from inside a separate dependency.
        """
        yield from _get_db(self.cached_sessionmaker)

    @asynccontextmanager
    def context_session(self) -> AsyncIterator[AsyncSession]:
        """
        A context-manager wrapped version of the `get_db` method.

        This makes it possible to get a context-managed orm session for the relevant database_uri without
        needing to rely on FastAPI's dependency injection.
        """
        yield from self.get_db()

    def reset_cache(self) -> None:
        """
        Resets the engine and sessionmaker caches.

        After calling this method, the next time you try to use the cached engine or sessionmaker,
        new ones will be created.
        """
        self._cached_engine = None
        self._cached_sessionmaker = None


def get_engine(uri: str) -> AsyncEngine:
    """
    Returns a sqlalchemy engine with pool_pre_ping enabled.

    This function may be updated over time to reflect recommended engine configuration for use with FastAPI.
    """
    return create_async_engine(uri, pool_pre_ping=True, poolclass=AsyncAdaptedQueuePool)


def get_sessionmaker_for_engine(engine: AsyncEngine) -> async_sessionmaker:
    """
    Returns a sqlalchemy sessionmaker for the provided engine with recommended configuration settings.

    This function may be updated over time to reflect recommended sessionmaker configuration for use with FastAPI.
    """
    return async_sessionmaker(bind=engine, expire_on_commit=False)


@asynccontextmanager
def context_session(engine: AsyncEngine) -> AsyncIterator[AsyncSession]:
    """
    This contextmanager yields a managed session for the provided engine.

    Usage is similar to `AsyncSessionMaker.context_session`, except that you have to provide the engine to use.

    A new sessionmaker is created for each call, so the AsyncSessionMaker.context_session
    method may be preferable in performance-sensitive contexts.
    """
    sessionmaker = get_sessionmaker_for_engine(engine)
    yield from _get_db(sessionmaker)


def _get_db(sessionmaker: async_sessionmaker) -> AsyncIterator[AsyncSession]:
    """
    A generator function that yields an ORM session using the provided sessionmaker, and cleans it up when resumed.
    """
    session = sessionmaker()
    try:
        yield session
        session.commit()
    except Exception as exc:
        session.rollback()
        raise exc
    finally:
        session.close()
