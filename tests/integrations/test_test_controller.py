import asyncio

import pytest
from httpx import AsyncClient


class TestTestController:
    async def test_concurrent_requests(self, async_client: AsyncClient):
        tested = False
        tasks = [async_client.get("/test/sleep") for _ in range(10)]
        responses = await asyncio.gather(*tasks)
        for response in responses:
            assert response.status_code == 200
            tested = True

        assert tested

    async def test_exception(self, async_client: AsyncClient):
        with pytest.raises(ValueError):
            await async_client.get("/test/exception")


