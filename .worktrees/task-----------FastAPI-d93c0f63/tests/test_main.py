import httpx
import pytest
from fastapi import status

from app.main import app


@pytest.fixture
def client():
    return httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
    )


@pytest.mark.asyncio
async def test_health_endpoint(client: httpx.AsyncClient):
    async with client as c:
        response = await c.get("/health")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "ok"
    assert "app" in data
