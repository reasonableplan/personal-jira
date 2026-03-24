import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_health_check_status_code(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200


@pytest.mark.anyio
async def test_health_check_response_body(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.json() == {"status": "ok"}
