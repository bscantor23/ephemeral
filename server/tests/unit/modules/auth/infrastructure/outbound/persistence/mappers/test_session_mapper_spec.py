from datetime import datetime, timezone
from uuid import uuid4

from app.commons.db.schemas.session_schema import SessionSchema
from app.modules.auth.domain.entities.session_entity import SessionEntity
from app.modules.auth.infrastructure.outbound.persistence.mappers.session_mapper import (
    SessionMapper,
)


def test_session_mapper_to_schema_and_to_entity():
    """
    ↳ Mappers: SessionMapper transforma bidireccionalmente SessionEntity y SessionSchema
    """
    sid = uuid4()
    uid = uuid4()
    now = datetime.now(timezone.utc)
    entity = SessionEntity(
        id=sid,
        user_id=uid,
        token_hash="hash_session",
        expires_at=now,
        revoked_at=now,
        created_at=now,
    )
    schema = SessionMapper.to_schema(entity)
    assert schema.id == sid
    assert schema.user_id == uid
    assert schema.token_hash == "hash_session"
    assert schema.revoked_at == now

    converted = SessionMapper.to_entity(schema)
    assert converted.id == sid
    assert converted.user_id == uid
    assert converted.token_hash == "hash_session"
    assert converted.revoked_at == now

    vo_converted = SessionMapper.to_vo(schema)
    assert vo_converted.id == sid
