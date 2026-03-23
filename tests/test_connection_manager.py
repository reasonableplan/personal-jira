import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from personal_jira.services.connection_manager import ConnectionManager


@pytest.fixture
def manager() -> ConnectionManager:
    return ConnectionManager()


def _make_ws(client_id: str = "agent-1") -> AsyncMock:
    ws = AsyncMock()
    ws.client_state = MagicMock()
    ws.client_state.name = "CONNECTED"
    return ws


class TestConnect:
    async def test_connect_adds_to_active(self, manager: ConnectionManager) -> None:
        ws = _make_ws()
        await manager.connect(ws, client_id="agent-1")
        assert "agent-1" in manager.active_connections
        ws.accept.assert_awaited_once()

    async def test_connect_multiple_clients(self, manager: ConnectionManager) -> None:
        ws1, ws2 = _make_ws(), _make_ws()
        await manager.connect(ws1, client_id="agent-1")
        await manager.connect(ws2, client_id="agent-2")
        assert len(manager.active_connections) == 2


class TestDisconnect:
    async def test_disconnect_removes_from_active(self, manager: ConnectionManager) -> None:
        ws = _make_ws()
        await manager.connect(ws, client_id="agent-1")
        manager.disconnect(client_id="agent-1")
        assert "agent-1" not in manager.active_connections

    async def test_disconnect_nonexistent_is_noop(self, manager: ConnectionManager) -> None:
        manager.disconnect(client_id="nonexistent")
        assert len(manager.active_connections) == 0


class TestBroadcast:
    async def test_broadcast_sends_to_all(self, manager: ConnectionManager) -> None:
        ws1, ws2 = _make_ws(), _make_ws()
        await manager.connect(ws1, client_id="agent-1")
        await manager.connect(ws2, client_id="agent-2")
        message = {"type": "issue_updated", "issue_id": "abc"}
        await manager.broadcast(message)
        ws1.send_json.assert_awaited_once_with(message)
        ws2.send_json.assert_awaited_once_with(message)

    async def test_broadcast_skips_failed_and_removes(self, manager: ConnectionManager) -> None:
        ws1, ws2 = _make_ws(), _make_ws()
        await manager.connect(ws1, client_id="agent-1")
        await manager.connect(ws2, client_id="agent-2")
        ws1.send_json.side_effect = Exception("closed")
        message = {"type": "issue_updated", "issue_id": "abc"}
        await manager.broadcast(message)
        assert "agent-1" not in manager.active_connections
        ws2.send_json.assert_awaited_once_with(message)

    async def test_broadcast_empty_connections(self, manager: ConnectionManager) -> None:
        await manager.broadcast({"type": "test"})


class TestSendPersonal:
    async def test_send_personal_to_specific_client(self, manager: ConnectionManager) -> None:
        ws = _make_ws()
        await manager.connect(ws, client_id="agent-1")
        message = {"type": "assigned", "issue_id": "xyz"}
        await manager.send_personal(message, client_id="agent-1")
        ws.send_json.assert_awaited_once_with(message)

    async def test_send_personal_nonexistent_client(self, manager: ConnectionManager) -> None:
        await manager.send_personal({"type": "test"}, client_id="ghost")


class TestBroadcastExclude:
    async def test_broadcast_excludes_sender(self, manager: ConnectionManager) -> None:
        ws1, ws2 = _make_ws(), _make_ws()
        await manager.connect(ws1, client_id="agent-1")
        await manager.connect(ws2, client_id="agent-2")
        message = {"type": "issue_updated", "issue_id": "abc"}
        await manager.broadcast(message, exclude="agent-1")
        ws1.send_json.assert_not_awaited()
        ws2.send_json.assert_awaited_once_with(message)
