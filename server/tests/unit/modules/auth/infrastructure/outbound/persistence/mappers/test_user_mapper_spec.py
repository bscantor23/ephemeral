from datetime import datetime, timezone
from uuid import uuid4

from app.commons.db.schemas.user_schema import UserSchema
from app.modules.auth.domain.entities.user_entity import UserEntity
from app.modules.auth.infrastructure.outbound.persistence.mappers.user_mapper import (
    UserMapper,
)


def test_user_mapper_to_schema_and_to_entity():
    """
    ↳ Mappers: UserMapper transforma bidireccionalmente UserEntity y UserSchema
    """
    uid = uuid4()
    now = datetime.now(timezone.utc)
    entity = UserEntity(
        id=uid,
        username="alice",
        display_name="Alice",
        password_hash="pw_hash",
        identity_sign_pub="sp",
        identity_dh_pub="dp",
        identity_dh_sig="ds",
        created_at=now,
        updated_at=now,
    )
    schema = UserMapper.to_schema(entity)
    assert schema.id == uid
    assert schema.username == "alice"
    assert schema.password_hash == "pw_hash"

    converted = UserMapper.to_entity(schema)
    assert converted.id == uid
    assert converted.username == "alice"
    assert converted.password_hash == "pw_hash"

    vo_converted = UserMapper.to_vo(schema)
    assert vo_converted.id == uid
