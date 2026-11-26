from datetime import datetime, timezone
from uuid import uuid4

from app.modules.messages.domain.entities.message_entity import MessageEntity


def test_message_entity_create_and_mark_delivered():
    """
    ↳ MessageEntity se crea con delivered_at None y permite marcar delivered
    """
    session_id = uuid4()
    sender_id = uuid4()
    recipient_id = uuid4()
    spk_id = uuid4()

    entity = MessageEntity.create(
        chat_session_id=session_id,
        sender_id=sender_id,
        recipient_id=recipient_id,
        msg_num=0,
        ciphertext="base64_enc_payload",
        ephemeral_pub="b64_ephemeral_pub",
        signed_prekey_id=spk_id,
        protocol_version=1,
    )

    assert entity.id is not None
    assert entity.chat_session_id == session_id
    assert entity.sender_id == sender_id
    assert entity.recipient_id == recipient_id
    assert entity.msg_num == 0
    assert entity.ciphertext == "base64_enc_payload"
    assert entity.ephemeral_pub == "b64_ephemeral_pub"
    assert entity.signed_prekey_id == spk_id
    assert entity.protocol_version == 1
    assert entity.delivered_at is None
    assert isinstance(entity.created_at, datetime)

    delivered_time = datetime.now(timezone.utc)
    updated = entity.mark_delivered(delivered_time)

    assert updated.delivered_at == delivered_time
    assert updated.id == entity.id
    assert entity.delivered_at is None
