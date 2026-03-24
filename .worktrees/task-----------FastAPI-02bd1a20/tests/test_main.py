import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


def test_app_exists() -> None:
    assert app is not None
    assert app.title == "fastapi-app"


@pytest.mark.asyncio
async def test_health_endpoint() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
