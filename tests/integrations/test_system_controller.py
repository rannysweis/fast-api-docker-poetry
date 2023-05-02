from starlette.testclient import TestClient


class TestSettingController:
    def test_root(self, client: TestClient) -> None:
        status = 200
        response = client.get("/")
        assert response.status_code == status
        assert response.json() == {"message": "Hello World!"}

    def test_healthcheck(self, client: TestClient) -> None:
        status = 200
        response = client.get("/health")
        assert response.status_code == status
        assert response.json() == {"fast-api-docker-poetry": status}
