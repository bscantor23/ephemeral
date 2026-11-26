from datetime import datetime, timezone
from uuid import uuid4

from app.modules.messages.infrastructure.inbound.http.dto.message_response_dto import (
    MessageResponseDTO,
    PendingMessagesResponseDTO,
)
from app.modules.messages.infrastructure.inbound.http.dto.send_message_dto import (
    SendMessageRequestDTO,
)


def test_messages_dto():
    """
    ↳ DTOs de mensajes serializan y validan campos
    """
    sid = uuid4()
    rid = uuid4()
    session_id = uuid4()

    req = SendMessageRequestDTO(
        recipient_id=rid,
        chat_session_id=session_id,
        msg_num=0,
        ciphertext="payload",
    )
    assert req.recipient_id == rid
    assert req.protocol_version == 1

    resp = MessageResponseDTO(
        id=uuid4(),
        chat_session_id=session_id,
        sender_id=sid,
        recipient_id=rid,
        protocol_version=1,
        msg_num=0,
        ciphertext="payload",
        ephemeral_pub=None,
        signed_prekey_id=None,
        delivered_at=None,
        created_at=datetime.now(timezone.utc),
    )
    assert resp.msg_num == 0

    pending = PendingMessagesResponseDTO(messages=[resp], count=1)
    assert pending.count == 1
