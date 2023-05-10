from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from requests import HTTPError
from sqlalchemy.exc import IntegrityError, ProgrammingError, NoResultFound
from starlette.exceptions import HTTPException

from app.config import exception_config as exh
from app.config.settings import Environment, get_settings
from app.controllers.order_controller import order_router
from app.controllers.system_controller import system_router
from app.controllers.test_controller import test_router
from app.utils import db

settings = get_settings()


def create_application() -> FastAPI:
    application = FastAPI(
        title="Fast Api Docker Poetry Docs",
        debug=False,
    )

    if settings.environment == Environment.prod:
        application.openapi_url = None

    application.add_exception_handler(RequestValidationError, exh.req_validation_handler)
    application.add_exception_handler(ValidationError, exh.validation_handler)
    application.add_exception_handler(AttributeError, exh.attribute_error_handler)

    application.add_exception_handler(NoResultFound, exh.data_not_found_error_handler)
    application.add_exception_handler(IntegrityError, exh.sql_error_handler)
    application.add_exception_handler(ProgrammingError, exh.sql_error_handler)
    application.add_exception_handler(HTTPError, exh.http_error_handler)
    application.add_exception_handler(HTTPException, exh.http_exception_handler)

    application.include_router(system_router)
    application.include_router(order_router)

    if settings.is_local_dev:
        application.include_router(test_router)

    @application.on_event("startup")
    async def initialize():
        db.wait_for_postgres()

    @application.on_event("shutdown")
    async def shutdown():
        db.shutdown()

    return application


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:create_application",
        factory=True,
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level,
        access_log=True,
        reload=settings.is_local_dev,
    )
