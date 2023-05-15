import logging
import os

import alembic
import alembic.command
import alembic.config
import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient

from app.main import create_application


@pytest.fixture(scope="session")
def app() -> FastAPI:
    return create_application()


@pytest_asyncio.fixture
async def async_client(app: FastAPI) -> AsyncClient:
    async with AsyncClient(app=app, base_url='http://test') as client:
        yield client


@pytest.fixture(autouse=True)
def run_migrations() -> None:
    logging.getLogger('alembic').setLevel(logging.WARNING)
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    cfg = alembic.config.Config(os.path.join(project_root, "alembic.ini"))
    cfg.set_main_option(
        "script_location", os.path.join(project_root, "migrations")
    )
    alembic.command.upgrade(cfg, "head")
    yield
    alembic.command.downgrade(cfg, "base")
