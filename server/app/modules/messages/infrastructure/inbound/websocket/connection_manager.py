from collections import defaultdict
from typing import Any
from uuid import UUID
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self._active_connections: dict[UUID, set[WebSocket]] = defaultdict(set)

    async def connect(self, user_id: UUID, websocket: WebSocket) -> None:
        await websocket.accept()
        self._active_connections[user_id].add(websocket)

    def disconnect(self, user_id: UUID, websocket: WebSocket) -> None:
        if user_id in self._active_connections:
            self._active_connections[user_id].discard(websocket)
            if not self._active_connections[user_id]:
                del self._active_connections[user_id]

    def is_user_online(self, user_id: UUID) -> bool:
        return bool(self._active_connections.get(user_id))

    async def send_json_to_user(self, user_id: UUID, data: Any) -> bool:
        connections = self._active_connections.get(user_id)
        if not connections:
            return False

        dead_sockets: list[WebSocket] = []
        delivered = False

        for socket in list(connections):
            try:
                await socket.send_json(data)
                delivered = True
            except Exception:
                dead_sockets.append(socket)

        for dead in dead_sockets:
            self.disconnect(user_id, dead)

        return delivered


global_connection_manager = ConnectionManager()
