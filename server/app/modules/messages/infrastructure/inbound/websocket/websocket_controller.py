from typing import Optional
from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect, status

from app.modules.auth.application.ports.validate_token_port import ValidateTokenPort
from app.modules.auth.infrastructure.outbound.security.auth_security import (
    get_validate_token_use_case,
)
from app.modules.messages.infrastructure.inbound.websocket.connection_manager import (
    ConnectionManager,
    global_connection_manager,
)

ws_router = APIRouter(tags=["WebSocket"])


@ws_router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(default=None),
    validate_use_case: ValidateTokenPort = Depends(get_validate_token_use_case),
) -> None:
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    try:
        user = validate_use_case.execute(token)
    except Exception:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    manager: ConnectionManager = global_connection_manager
    await manager.connect(user.id, websocket)

    try:
        while True:
            data = await websocket.receive_json()
            if isinstance(data, dict) and data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        manager.disconnect(user.id, websocket)
    except Exception:
        manager.disconnect(user.id, websocket)
