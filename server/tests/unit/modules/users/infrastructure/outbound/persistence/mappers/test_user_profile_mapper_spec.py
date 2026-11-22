from datetime import datetime, timezone
from uuid import uuid4

from app.commons.db.schemas.user_schema import UserSchema
from app.modules.users.domain.value_objects.user_profile_vo import UserProfileVO
from app.modules.users.infrastructure.outbound.persistence.mappers.user_profile_mapper import (
    UserProfileMapper,
)


def test_user_profile_mapper():
    """
    ↳ UserProfileMapper mapea entre UserSchema, Entity y DTO
    """
    uid = uuid4()
    now = datetime.now(timezone.utc)
    schema = UserSchema(
        id=uid,
        username="alice",
        display_name="Alice",
        password_hash="hash",
        identity_sign_pub="sig_pub",
        identity_dh_pub="dh_pub",
        identity_dh_sig="dh_sig",
        created_at=now,
        updated_at=now,
    )

    entity = UserProfileMapper.to_entity(schema, has_active_prekey=True)
    assert entity.id == uid
    assert entity.username == "alice"
    assert entity.has_active_prekey is True

    vo = UserProfileVO(
        id=entity.id,
        username=entity.username,
        display_name=entity.display_name,
        identity_sign_pub=entity.identity_sign_pub,
        identity_dh_pub=entity.identity_dh_pub,
        has_active_prekey=True,
        created_at=now,
    )
    dto = UserProfileMapper.to_dto(vo)
    assert dto.id == uid
    assert dto.has_active_prekey is True
