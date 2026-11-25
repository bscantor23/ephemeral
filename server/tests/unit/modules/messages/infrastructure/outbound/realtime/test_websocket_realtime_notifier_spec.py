from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
import pytest

from app.modules.messages.domain.value_objects.message_response_vo import (
    MessageResponseVO,
)
from app.modules.messages.infrastructure.outbound.realtime.websocket_realtime_notifier import (
    WebSocketRealtimeNotifier,
)


@pytest.mark.anyio
async def test_websocket_realtime_notifier():
    """
    ↳ WebSocketRealtimeNotifier formatea payload y llama send_json_to_user
    """
    manager_mock = MagicMock()
    manager_mock.send_json_to_user = AsyncMock(return_value=True)

    notifier = WebSocketRealtimeNotifier(connection_manager=manager_mock)

    rid = uuid4()
    vo = MessageResponseVO(
        id=uuid4(),
        chat_session_id=uuid4(),
        sender_id=uuid4(),
        recipient_id=rid,
        protocol_version=1,
        msg_num=0,
        ciphertext="encrypted_gcm",
        ephemeral_pub="eph_pub",
        signed_prekey_id=uuid4(),
        delivered_at=None,
        created_at=datetime.now(timezone.utc),
    )

    result = await notifier.notify_message(rid, vo)
    assert result is True
    manager_mock.send_json_to_user.assert_awaited_once()
    args, _ = manager_mock.send_json_to_user.call_args
    assert args[0] == rid
    assert args[1]["type"] == "message.incoming"
    assert args[1]["data"]["ciphertext"] == "encrypted_gcm"
