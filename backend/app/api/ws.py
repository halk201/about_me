from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.ws_service import WsReplayBuffer

router = APIRouter(tags=["ws"])
buffer = WsReplayBuffer()


@router.get("/v1/ws/replay/{seq}")
def replay(seq: int) -> list[dict]:
    return buffer.replay_from(seq)


@router.websocket("/v1/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            event = buffer.publish(data.get("channel", "general"), data.get("payload", {}))
            await websocket.send_json(event)
    except WebSocketDisconnect:
        return
