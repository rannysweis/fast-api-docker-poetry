from typing import Dict

from fastapi import status, APIRouter
from fastapi.responses import JSONResponse
from fastapi_utils.cbv import cbv

system_router = APIRouter()


@cbv(system_router)
class SystemController:

    @system_router.get("/", include_in_schema=False)
    async def root(self) -> Dict[str, str]:
        """Display welcome message."""
        return {"message": "Hello World!"}

    @system_router.get("/health", include_in_schema=False)
    async def healthcheck(self) -> JSONResponse:
        data = {"fast-api-docker-poetry": status.HTTP_200_OK}
        return JSONResponse(data, status_code=status.HTTP_200_OK)
