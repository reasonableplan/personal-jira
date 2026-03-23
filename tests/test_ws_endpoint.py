import pytest
from httpx import ASGITransport, AsyncClient
from starlette.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from personal_jira.app import create_app
from personal_jira.services.connection_manager import ConnectionManager


@pytest.fixture
def app():
    return create_app()


class TestWebSocketEndpoint:
    def test_ws_connect_without_client_id_rejected(self, app) -> None:
        client = TestClient(app)
        with pytest.raises(Exception):
            with client.websocket_connect("/ws"):
                pass

    def test_ws_connect_with_client_id(self, app) -> None:
        client = TestClient(app)
        with client.websocket_connect("/ws?client_id=agent-1") as ws:
            ws.send_json({"type": "ping"})
            resp = ws.receive_json()
            assert resp["type"] == "pong"

    def test_ws_broadcast_on_connect(self, app) -> None:
        client = TestClient(app)
        with client.websocket_connect("/ws?client_id=agent-1") as ws:
            data = ws.receive_json()
            assert data["type"] == "connection_established"
            assert data["client_id"] == "agent-1"

    def test_ws_multiple_clients(self, app) -> None:
        client = TestClient(app)
        with client.websocket_connect("/ws?client_id=agent-1") as ws1:
            ws1.receive_json()  # connection_established
            with client.websocket_connect("/ws?client_id=agent-2") as ws2:
                ws2.receive_json()  # connection_established
                ws1.send_json({"type": "ping"})
                resp = ws1.receive_json()
                assert resp["type"] == "pong"
