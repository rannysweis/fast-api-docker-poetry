import json
import logging

from fastapi.encoders import jsonable_encoder
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_404_NOT_FOUND

logger = logging.getLogger(__name__)


def _build_validation_errors(exc, title):
    return {
        "errors": [
            {
                "title": title,
                "source": "/".join(map(str, error["loc"])),
                "msg": error["msg"],
            }
            for error in exc.errors()
        ]
    }


def _build_error_dict(title, msg):
    return {
        "errors": [
            {
                "title": title,
                "msg": msg,
            }
        ]
    }


async def req_validation_handler(request, exc):
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(
            _build_validation_errors(exc, "Request Validation Error")
        ),
    )


async def validation_handler(request, exc):
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(
            _build_validation_errors(exc, "Validation Error")
        ),
    )


async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder(
            _build_error_dict("HTTP Exception", exc.detail)
        ),
    )


async def http_error_handler(request, exc):
    data = json.loads(exc.response.text)
    message = "Error"
    if "error_message" in data:
        message = data['error_message']
    elif "message" in data:
        message = data['message']

    logger.exception(f"{message} : {exc.response.url}")
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content=jsonable_encoder(
            _build_error_dict("Http Error", exc.detail)
        )
    )


async def unhandled_exception_handler(request: Request, exc):
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content=jsonable_encoder(
            _build_error_dict("Internal Server Error", "Internal Server Error")
        )
    )


async def attribute_error_handler(request, exc):
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(
            _build_error_dict("Attribute Error", str(exc))
        )
    )


async def sql_error_handler(request, exc):
    logger.exception(str(exc.orig))
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content=jsonable_encoder(
            _build_error_dict("Internal Server Error", "Database error occurred")
        )
    )


async def data_not_found_error_handler(request, exc):
    return JSONResponse(
        status_code=HTTP_404_NOT_FOUND,
        content=jsonable_encoder(
            _build_error_dict("Not Found Error", str(exc))
        )
    )
