import pytest
from httpx import ASGITransport, AsyncClient

from personal_jira.app import create_app


class TestCreateApp:
    def test_create_app_returns_fastapi(self) -> None:
        from fastapi import FastAPI

        app = create_app()
        assert isinstance(app, FastAPI)

    def test_app_title(self) -> None:
        app = create_app()
        assert app.title == "personal-jira"


class TestHealthEndpoint:
    @pytest.fixture()
    def app(self):
        return create_app()

    async def test_health_returns_200(self, app) -> None:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get("/health")
        assert resp.status_code == 200

    async def test_health_response_body(self, app) -> None:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get("/health")
        data = resp.json()
        assert data["status"] == "ok"
