import logging

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from personal_jira.dependencies import get_connection_manager

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    client_id: str = Query(...),
) -> None:
    manager = get_connection_manager()
    await manager.connect(websocket, client_id=client_id)
    try:
        await websocket.send_json({
            "type": "connection_established",
            "client_id": client_id,
        })
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")
            if msg_type == "ping":
                await websocket.send_json({"type": "pong"})
            else:
                logger.debug("Received from %s: %s", client_id, msg_type)
    except WebSocketDisconnect:
        manager.disconnect(client_id=client_id)
    except Exception:
        logger.exception("WebSocket error for %s", client_id)
        manager.disconnect(client_id=client_id)
