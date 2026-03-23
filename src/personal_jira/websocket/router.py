import json
import logging
import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from personal_jira.websocket.connection_manager import manager
from personal_jira.websocket.schemas import WSMessageType

logger = logging.getLogger(__name__)
router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    connection_id = str(uuid.uuid4())
    await manager.connect(connection_id, websocket)
    try:
        while True:
            raw = await websocket.receive_text()
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                await websocket.send_json(
                    {"type": WSMessageType.ERROR, "payload": {"message": "invalid JSON"}}
                )
                continue

            msg_type = data.get("type")
            payload = data.get("payload", {})

            if msg_type == WSMessageType.PING:
                await websocket.send_json({"type": WSMessageType.PONG, "payload": {}})
            elif msg_type == WSMessageType.SUBSCRIBE:
                channel = payload.get("channel", "")
                manager.subscribe(connection_id, channel)
                await websocket.send_json(
                    {"type": WSMessageType.SUBSCRIBED, "payload": {"channel": channel}}
                )
            elif msg_type == WSMessageType.UNSUBSCRIBE:
                channel = payload.get("channel", "")
                manager.unsubscribe(connection_id, channel)
                await websocket.send_json(
                    {
                        "type": WSMessageType.UNSUBSCRIBED,
                        "payload": {"channel": channel},
                    }
                )
            else:
                await websocket.send_json(
                    {
                        "type": WSMessageType.ERROR,
                        "payload": {"message": f"unknown type: {msg_type}"},
                    }
                )
    except WebSocketDisconnect:
        manager.disconnect(connection_id)
        logger.info("Client %s disconnected", connection_id)
