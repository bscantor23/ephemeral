from datetime import datetime, timezone
from uuid import uuid4

from app.commons.db.schemas.message_schema import MessageSchema
from app.modules.messages.domain.entities.message_entity import MessageEntity
from app.modules.messages.domain.value_objects.message_response_vo import (
    MessageResponseVO,
)
from app.modules.messages.infrastructure.outbound.persistence.mappers.message_mapper import (
    MessageMapper,
)


def test_message_mapper():
    """
    ↳ MessageMapper mapea entre Schema, Entity, VO y DTO
    """
    mid = uuid4()
    session_id = uuid4()
    sid = uuid4()
    rid = uuid4()
    now = datetime.now(timezone.utc)

    schema = MessageSchema(
        id=mid,
        chat_session_id=session_id,
        sender_id=sid,
        recipient_id=rid,
        protocol_version=1,
        msg_num=0,
        ciphertext="enc",
        ephemeral_pub="eph",
        signed_prekey_id=None,
        delivered_at=None,
        created_at=now,
    )

    entity = MessageMapper.to_entity(schema)
    assert entity.id == mid
    assert entity.ciphertext == "enc"

    back_schema = MessageMapper.to_schema(entity)
    assert back_schema.id == mid

    vo = MessageResponseVO(
        id=mid,
        chat_session_id=session_id,
        sender_id=sid,
        recipient_id=rid,
        protocol_version=1,
        msg_num=0,
        ciphertext="enc",
        ephemeral_pub="eph",
        signed_prekey_id=None,
        delivered_at=None,
        created_at=now,
    )
    dto = MessageMapper.to_dto(vo)
    assert dto.id == mid
