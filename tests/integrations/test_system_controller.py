from httpx import AsyncClient


class TestSettingController:
    async def test_root(self, async_client: AsyncClient) -> None:
        response = await async_client.get("/")

        assert response.status_code == 200
        assert response.json() == {"message": "Hello World!"}

    async def test_healthcheck(self, async_client: AsyncClient) -> None:
        response = await async_client.get("/health")

        assert response.status_code == 200
        assert response.json() == {"fast-api-docker-poetry": 200}
