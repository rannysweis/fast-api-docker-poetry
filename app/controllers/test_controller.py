import asyncio
from typing import Dict

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi_restful.cbv import cbv

test_router = APIRouter()


@cbv(test_router)
class TestController:

    @test_router.get("/test/sleep", include_in_schema=False)
    async def sleep_test(self) -> Dict[str, str]:
        await asyncio.sleep(1)
        return {"message": "Hello World!"}

    @test_router.get("/test/exception", include_in_schema=False)
    async def exception_test(self) -> JSONResponse:
        raise ValueError("Something went wrong")
