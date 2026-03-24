from unittest.mock import AsyncMock, patch

import pytest
from app.main import app
from httpx import ASGITransport, AsyncClient


def test_app_exists() -> None:
    assert app is not None
    assert app.title == "fastapi-app"


@pytest.mark.asyncio
async def test_health_endpoint() -> None:
    mock_session = AsyncMock()
    mock_session.execute = AsyncMock()

    mock_gen = AsyncMock()
    mock_gen.__aenter__ = AsyncMock(return_value=mock_session)
    mock_gen.__aexit__ = AsyncMock(return_value=False)

    with patch("app.routers.health.async_session_factory", return_value=mock_gen):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/health")
    assert resp.status_code == 200
