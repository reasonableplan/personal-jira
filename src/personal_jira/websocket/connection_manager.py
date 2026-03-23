import logging
from typing import Any

from starlette.websockets import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: dict[str, WebSocket] = {}
        self.subscriptions: dict[str, set[str]] = {}

    async def connect(self, connection_id: str, websocket: WebSocket) -> None:
        self.active_connections[connection_id] = websocket
        self.subscriptions[connection_id] = set()

    def disconnect(self, connection_id: str) -> None:
        self.active_connections.pop(connection_id, None)
        self.subscriptions.pop(connection_id, None)

    def subscribe(self, connection_id: str, channel: str) -> None:
        if connection_id in self.subscriptions:
            self.subscriptions[connection_id].add(channel)

    def unsubscribe(self, connection_id: str, channel: str) -> None:
        if connection_id in self.subscriptions:
            self.subscriptions[connection_id].discard(channel)

    async def send_personal_message(
        self, connection_id: str, message: dict[str, Any]
    ) -> None:
        ws = self.active_connections[connection_id]
        await ws.send_json(message)

    async def broadcast(self, message: dict[str, Any]) -> None:
        disconnected: list[str] = []
        for conn_id, ws in self.active_connections.items():
            try:
                await ws.send_json(message)
            except Exception:
                logger.warning("Failed to send to %s, removing connection", conn_id)
                disconnected.append(conn_id)
        for conn_id in disconnected:
            self.disconnect(conn_id)

    async def broadcast_to_channel(
        self, channel: str, message: dict[str, Any]
    ) -> None:
        disconnected: list[str] = []
        for conn_id, channels in self.subscriptions.items():
            if channel in channels:
                try:
                    await self.active_connections[conn_id].send_json(message)
                except Exception:
                    logger.warning(
                        "Failed to send to %s on channel %s", conn_id, channel
                    )
                    disconnected.append(conn_id)
        for conn_id in disconnected:
            self.disconnect(conn_id)


manager = ConnectionManager()
