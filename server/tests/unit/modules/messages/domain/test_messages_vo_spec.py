from datetime import datetime, timezone
from uuid import uuid4

from app.modules.messages.domain.value_objects.message_response_vo import (
    MessageResponseVO,
)
from app.modules.messages.domain.value_objects.pending_messages_response_vo import (
    PendingMessagesResponseVO,
)
from app.modules.messages.domain.value_objects.send_message_request_vo import (
    SendMessageRequestVO,
)


def test_messages_value_objects():
    """
    ↳ Value objects encapsulan request y response inmutables
    """
    mid = uuid4()
    sid = uuid4()
    rid = uuid4()
    session_id = uuid4()
    spk_id = uuid4()
    now = datetime.now(timezone.utc)

    req = SendMessageRequestVO(
        recipient_id=rid,
        chat_session_id=session_id,
        msg_num=1,
        ciphertext="payload",
        ephemeral_pub="eph",
        signed_prekey_id=spk_id,
        protocol_version=1,
    )
    assert req.recipient_id == rid
    assert req.msg_num == 1

    resp = MessageResponseVO(
        id=mid,
        chat_session_id=session_id,
        sender_id=sid,
        recipient_id=rid,
        protocol_version=1,
        msg_num=1,
        ciphertext="payload",
        ephemeral_pub="eph",
        signed_prekey_id=spk_id,
        delivered_at=None,
        created_at=now,
    )
    assert resp.id == mid
    assert resp.delivered_at is None

    pending = PendingMessagesResponseVO(messages=[resp], count=1)
    assert len(pending.messages) == 1
    assert pending.count == 1
