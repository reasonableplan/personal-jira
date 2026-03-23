import logging
from typing import Any

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, *, client_id: str) -> None:
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info("Client connected: %s (total: %d)", client_id, len(self.active_connections))

    def disconnect(self, *, client_id: str) -> None:
        removed = self.active_connections.pop(client_id, None)
        if removed:
            logger.info("Client disconnected: %s (total: %d)", client_id, len(self.active_connections))

    async def send_personal(self, message: dict[str, Any], *, client_id: str) -> None:
        ws = self.active_connections.get(client_id)
        if ws is None:
            return
        try:
            await ws.send_json(message)
        except Exception:
            logger.warning("Failed to send to %s, removing", client_id)
            self.disconnect(client_id=client_id)

    async def broadcast(
        self, message: dict[str, Any], *, exclude: str | None = None
    ) -> None:
        disconnected: list[str] = []
        for cid, ws in self.active_connections.items():
            if cid == exclude:
                continue
            try:
                await ws.send_json(message)
            except Exception:
                logger.warning("Broadcast failed for %s, marking for removal", cid)
                disconnected.append(cid)
        for cid in disconnected:
            self.disconnect(client_id=cid)
