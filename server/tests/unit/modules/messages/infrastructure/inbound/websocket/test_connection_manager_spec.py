from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
import pytest

from app.modules.messages.infrastructure.inbound.websocket.connection_manager import (
    ConnectionManager,
)


@pytest.mark.anyio
async def test_connection_manager_lifecycle():
    """
    ↳ ConnectionManager conecta, rastrea estado online y desconecta sockets
    """
    manager = ConnectionManager()
    uid = uuid4()
    ws1 = MagicMock()
    ws1.accept = AsyncMock()
    ws1.send_json = AsyncMock()

    assert not manager.is_user_online(uid)

    await manager.connect(uid, ws1)
    assert manager.is_user_online(uid)

    success = await manager.send_json_to_user(uid, {"type": "ping"})
    assert success is True
    ws1.send_json.assert_awaited_once_with({"type": "ping"})

    manager.disconnect(uid, ws1)
    assert not manager.is_user_online(uid)


@pytest.mark.anyio
async def test_connection_manager_send_offline_and_dead_socket():
    """
    ↳ send_json_to_user maneja usuarios offline y sockets desconectados
    """
    manager = ConnectionManager()
    uid = uuid4()

    assert await manager.send_json_to_user(uid, {"test": 1}) is False

    dead_ws = MagicMock()
    dead_ws.accept = AsyncMock()
    dead_ws.send_json = AsyncMock(side_effect=Exception("Broken pipe"))

    await manager.connect(uid, dead_ws)
    assert await manager.send_json_to_user(uid, {"test": 2}) is False
    assert not manager.is_user_online(uid)
