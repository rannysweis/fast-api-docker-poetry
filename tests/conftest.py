import logging
import os

import alembic
import alembic.command
import alembic.config
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.main import create_application


@pytest.fixture(scope="session")
def app() -> FastAPI:
    return create_application()


@pytest.fixture(scope="session")
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


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
