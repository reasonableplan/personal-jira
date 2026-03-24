import httpx
import pytest


@pytest.mark.anyio
async def test_health_returns_200(client: httpx.AsyncClient) -> None:
    resp = await client.get("/health")
    assert resp.status_code == 200


@pytest.mark.anyio
async def test_health_body(client: httpx.AsyncClient) -> None:
    resp = await client.get("/health")
    body = resp.json()
    assert body["status"] == "ok"
