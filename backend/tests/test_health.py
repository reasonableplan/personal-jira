import pytest
from app.main import app
from httpx import ASGITransport, AsyncClient


@pytest.mark.anyio
async def test_health_returns_200() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"


@pytest.mark.anyio
async def test_health_response_shape() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health")
    body = resp.json()
    assert set(body.keys()) == {"status"}
