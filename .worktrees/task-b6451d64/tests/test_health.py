from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_health_ok(client: AsyncClient) -> None:
    mock_result = AsyncMock()
    mock_result.scalar_one.return_value = 1

    mock_session = AsyncMock()
    mock_session.execute.return_value = mock_result
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)

    with patch("app.api.health.async_session_factory", return_value=mock_session):
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "connected"}


@pytest.mark.anyio
async def test_health_db_disconnected(client: AsyncClient) -> None:
    mock_session = AsyncMock()
    mock_session.execute.side_effect = ConnectionRefusedError("connection refused")
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)

    with patch("app.api.health.async_session_factory", return_value=mock_session):
        response = await client.get("/health")

    assert response.status_code == 503
    data = response.json()
    assert data["status"] == "error"
    assert data["database"] == "disconnected"
    assert "connection refused" in data["detail"]


@pytest.mark.anyio
async def test_health_db_generic_error(client: AsyncClient) -> None:
    mock_session = AsyncMock()
    mock_session.execute.side_effect = Exception("timeout")
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)

    with patch("app.api.health.async_session_factory", return_value=mock_session):
        response = await client.get("/health")

    assert response.status_code == 503
    data = response.json()
    assert data["status"] == "error"
    assert data["database"] == "disconnected"
    assert "timeout" in data["detail"]
