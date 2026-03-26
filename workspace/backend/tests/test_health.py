from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routers.health import router


@pytest.fixture()
def client():
    """Create a minimal test app with just the health router (no lifespan DB check)."""
    test_app = FastAPI()
    test_app.include_router(router)
    with TestClient(test_app) as c:
        yield c


class TestHealthEndpoint:
    """GET /health 엔드포인트 테스트."""

    def test_health_returns_200(self, client: TestClient):
        """Health endpoint always returns 200."""
        with patch("app.routers.health.get_engine") as mock_get_engine:
            mock_conn = AsyncMock()
            mock_conn.execute = AsyncMock()
            mock_engine = MagicMock()
            mock_engine.connect = MagicMock(return_value=AsyncMock(
                __aenter__=AsyncMock(return_value=mock_conn),
                __aexit__=AsyncMock(return_value=False),
            ))
            mock_get_engine.return_value = mock_engine

            response = client.get("/health")

        assert response.status_code == 200

    def test_health_db_connected(self, client: TestClient):
        """DB 연결 성공 시 database: connected."""
        with patch("app.routers.health.get_engine") as mock_get_engine:
            mock_conn = AsyncMock()
            mock_conn.execute = AsyncMock()
            mock_engine = MagicMock()
            mock_engine.connect = MagicMock(return_value=AsyncMock(
                __aenter__=AsyncMock(return_value=mock_conn),
                __aexit__=AsyncMock(return_value=False),
            ))
            mock_get_engine.return_value = mock_engine

            response = client.get("/health")

        data = response.json()
        assert data["status"] == "ok"
        assert data["database"] == "connected"

    def test_health_db_disconnected(self, client: TestClient):
        """DB 연결 실패 시 database: disconnected."""
        with patch("app.routers.health.get_engine") as mock_get_engine:
            mock_engine = MagicMock()
            mock_engine.connect = MagicMock(return_value=AsyncMock(
                __aenter__=AsyncMock(side_effect=ConnectionRefusedError("DB down")),
                __aexit__=AsyncMock(return_value=False),
            ))
            mock_get_engine.return_value = mock_engine

            response = client.get("/health")

        data = response.json()
        assert response.status_code == 200
        assert data["status"] == "ok"
        assert data["database"] == "disconnected"

    def test_health_response_shape(self, client: TestClient):
        """응답에 status와 database 키만 포함."""
        with patch("app.routers.health.get_engine") as mock_get_engine:
            mock_conn = AsyncMock()
            mock_conn.execute = AsyncMock()
            mock_engine = MagicMock()
            mock_engine.connect = MagicMock(return_value=AsyncMock(
                __aenter__=AsyncMock(return_value=mock_conn),
                __aexit__=AsyncMock(return_value=False),
            ))
            mock_get_engine.return_value = mock_engine

            response = client.get("/health")

        data = response.json()
        assert set(data.keys()) == {"status", "database"}
