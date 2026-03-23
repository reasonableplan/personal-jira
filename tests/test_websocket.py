import asyncio
import uuid
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient
from starlette.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from personal_jira.main import app
from personal_jira.websocket.connection_manager import ConnectionManager
from personal_jira.websocket.schemas import (
    WSMessage,
    WSMessageType,
    SubscribePayload,
    UnsubscribePayload,
)


@pytest.fixture
def manager() -> ConnectionManager:
    return ConnectionManager()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


class TestConnectionManager:
    async def test_connect_adds_connection(self, manager: ConnectionManager) -> None:
        ws = AsyncMock()
        conn_id = str(uuid.uuid4())
        await manager.connect(conn_id, ws)
        assert conn_id in manager.active_connections

    async def test_disconnect_removes_connection(self, manager: ConnectionManager) -> None:
        ws = AsyncMock()
        conn_id = str(uuid.uuid4())
        await manager.connect(conn_id, ws)
        manager.disconnect(conn_id)
        assert conn_id not in manager.active_connections

    async def test_disconnect_nonexistent_is_noop(self, manager: ConnectionManager) -> None:
        manager.disconnect("nonexistent")
        assert len(manager.active_connections) == 0

    async def test_send_personal_message(self, manager: ConnectionManager) -> None:
        ws = AsyncMock()
        conn_id = str(uuid.uuid4())
        await manager.connect(conn_id, ws)
        message = {"type": "issue_updated", "data": {"id": "123"}}
        await manager.send_personal_message(conn_id, message)
        ws.send_json.assert_called_once_with(message)

    async def test_send_personal_message_unknown_id(self, manager: ConnectionManager) -> None:
        with pytest.raises(KeyError):
            await manager.send_personal_message("unknown", {"msg": "hi"})

    async def test_broadcast(self, manager: ConnectionManager) -> None:
        ws1 = AsyncMock()
        ws2 = AsyncMock()
        id1, id2 = str(uuid.uuid4()), str(uuid.uuid4())
        await manager.connect(id1, ws1)
        await manager.connect(id2, ws2)
        message = {"type": "broadcast", "data": {}}
        await manager.broadcast(message)
        ws1.send_json.assert_called_once_with(message)
        ws2.send_json.assert_called_once_with(message)

    async def test_broadcast_skips_failed_connections(
        self, manager: ConnectionManager
    ) -> None:
        ws_ok = AsyncMock()
        ws_fail = AsyncMock()
        ws_fail.send_json.side_effect = Exception("connection lost")
        id_ok, id_fail = str(uuid.uuid4()), str(uuid.uuid4())
        await manager.connect(id_ok, ws_ok)
        await manager.connect(id_fail, ws_fail)
        message = {"type": "broadcast", "data": {}}
        await manager.broadcast(message)
        ws_ok.send_json.assert_called_once_with(message)
        assert id_fail not in manager.active_connections


class TestSubscription:
    async def test_subscribe_to_channel(self, manager: ConnectionManager) -> None:
        ws = AsyncMock()
        conn_id = str(uuid.uuid4())
        channel = "issues"
        await manager.connect(conn_id, ws)
        manager.subscribe(conn_id, channel)
        assert channel in manager.subscriptions.get(conn_id, set())

    async def test_unsubscribe_from_channel(self, manager: ConnectionManager) -> None:
        ws = AsyncMock()
        conn_id = str(uuid.uuid4())
        channel = "issues"
        await manager.connect(conn_id, ws)
        manager.subscribe(conn_id, channel)
        manager.unsubscribe(conn_id, channel)
        assert channel not in manager.subscriptions.get(conn_id, set())

    async def test_unsubscribe_nonexistent_channel_is_noop(
        self, manager: ConnectionManager
    ) -> None:
        ws = AsyncMock()
        conn_id = str(uuid.uuid4())
        await manager.connect(conn_id, ws)
        manager.unsubscribe(conn_id, "nonexistent")

    async def test_disconnect_cleans_up_subscriptions(
        self, manager: ConnectionManager
    ) -> None:
        ws = AsyncMock()
        conn_id = str(uuid.uuid4())
        await manager.connect(conn_id, ws)
        manager.subscribe(conn_id, "issues")
        manager.subscribe(conn_id, "comments")
        manager.disconnect(conn_id)
        assert conn_id not in manager.subscriptions

    async def test_broadcast_to_channel(self, manager: ConnectionManager) -> None:
        ws1 = AsyncMock()
        ws2 = AsyncMock()
        ws3 = AsyncMock()
        id1, id2, id3 = str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())
        await manager.connect(id1, ws1)
        await manager.connect(id2, ws2)
        await manager.connect(id3, ws3)
        manager.subscribe(id1, "issues")
        manager.subscribe(id2, "issues")
        message = {"type": "issue_created", "data": {"id": "456"}}
        await manager.broadcast_to_channel("issues", message)
        ws1.send_json.assert_called_once_with(message)
        ws2.send_json.assert_called_once_with(message)
        ws3.send_json.assert_not_called()

    async def test_broadcast_to_empty_channel(self, manager: ConnectionManager) -> None:
        message = {"type": "test", "data": {}}
        await manager.broadcast_to_channel("empty_channel", message)

    async def test_multiple_channels_per_connection(
        self, manager: ConnectionManager
    ) -> None:
        ws = AsyncMock()
        conn_id = str(uuid.uuid4())
        await manager.connect(conn_id, ws)
        manager.subscribe(conn_id, "issues")
        manager.subscribe(conn_id, "comments")
        subs = manager.subscriptions[conn_id]
        assert "issues" in subs
        assert "comments" in subs


class TestWSSchemas:
    def test_subscribe_message(self) -> None:
        msg = WSMessage(
            type=WSMessageType.SUBSCRIBE,
            payload=SubscribePayload(channel="issues"),
        )
        assert msg.type == WSMessageType.SUBSCRIBE
        assert msg.payload.channel == "issues"

    def test_unsubscribe_message(self) -> None:
        msg = WSMessage(
            type=WSMessageType.UNSUBSCRIBE,
            payload=UnsubscribePayload(channel="issues"),
        )
        assert msg.type == WSMessageType.UNSUBSCRIBE
        assert msg.payload.channel == "issues"

    def test_message_type_values(self) -> None:
        assert WSMessageType.SUBSCRIBE == "subscribe"
        assert WSMessageType.UNSUBSCRIBE == "unsubscribe"
        assert WSMessageType.PING == "ping"
        assert WSMessageType.PONG == "pong"
        assert WSMessageType.ERROR == "error"


class TestWebSocketEndpoint:
    def test_websocket_connect_and_receive(self, client: TestClient) -> None:
        with client.websocket_connect("/ws") as ws:
            ws.send_json({"type": "ping", "payload": {}})
            data = ws.receive_json()
            assert data["type"] == "pong"

    def test_websocket_subscribe(self, client: TestClient) -> None:
        with client.websocket_connect("/ws") as ws:
            ws.send_json({"type": "subscribe", "payload": {"channel": "issues"}})
            data = ws.receive_json()
            assert data["type"] == "subscribed"
            assert data["payload"]["channel"] == "issues"

    def test_websocket_unsubscribe(self, client: TestClient) -> None:
        with client.websocket_connect("/ws") as ws:
            ws.send_json({"type": "subscribe", "payload": {"channel": "issues"}})
            ws.receive_json()
            ws.send_json({"type": "unsubscribe", "payload": {"channel": "issues"}})
            data = ws.receive_json()
            assert data["type"] == "unsubscribed"
            assert data["payload"]["channel"] == "issues"

    def test_websocket_invalid_message_type(self, client: TestClient) -> None:
        with client.websocket_connect("/ws") as ws:
            ws.send_json({"type": "invalid_type", "payload": {}})
            data = ws.receive_json()
            assert data["type"] == "error"
            assert "message" in data["payload"]

    def test_websocket_malformed_json(self, client: TestClient) -> None:
        with client.websocket_connect("/ws") as ws:
            ws.send_text("not-json")
            data = ws.receive_json()
            assert data["type"] == "error"

    def test_websocket_disconnect_cleanup(self, client: TestClient) -> None:
        from personal_jira.websocket.connection_manager import manager

        initial_count = len(manager.active_connections)
        with client.websocket_connect("/ws"):
            assert len(manager.active_connections) == initial_count + 1
        assert len(manager.active_connections) == initial_count
