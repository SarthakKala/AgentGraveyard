from collections import defaultdict

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()
_connections: dict[str, set[WebSocket]] = defaultdict(set)


@router.websocket("/ws/{api_key_hash}")
async def graveyard_socket(websocket: WebSocket, api_key_hash: str):
    await websocket.accept()
    _connections[api_key_hash].add(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        _connections[api_key_hash].discard(websocket)


async def broadcast_event(api_key_hash: str, payload: dict) -> None:
    dead: list[WebSocket] = []
    for ws in _connections.get(api_key_hash, set()):
        try:
            await ws.send_json(payload)
        except Exception:
            dead.append(ws)
    for ws in dead:
        _connections[api_key_hash].discard(ws)
