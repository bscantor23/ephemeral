from datetime import datetime, timezone
from uuid import uuid4

from app.commons.db.schemas.prekey_bundle_schema import PrekeyBundleSchema
from app.modules.keys.domain.entities.prekey_bundle_entity import (
    PrekeyBundleEntity,
)
from app.modules.keys.infrastructure.outbound.persistence.mappers.prekey_bundle_mapper import (
    PrekeyBundleMapper,
)


def test_prekey_bundle_mapper_to_entity():
    """
    ↳ PrekeyBundleMapper.to_entity: mapea de ORM PrekeyBundleSchema a PrekeyBundleEntity
    """
    pk_id = uuid4()
    u_id = uuid4()
    now = datetime.now(timezone.utc)
    schema = PrekeyBundleSchema(
        id=pk_id,
        user_id=u_id,
        signed_prekey_pub="spk_pub",
        signature="spk_sig",
        is_active=True,
        created_at=now,
        expires_at=now,
    )

    entity = PrekeyBundleMapper.to_entity(schema)
    assert entity.id == pk_id
    assert entity.user_id == u_id
    assert entity.signed_prekey_pub == "spk_pub"
    assert entity.signature == "spk_sig"
    assert entity.is_active is True
    assert entity.created_at == now
    assert entity.expires_at == now


def test_prekey_bundle_mapper_to_schema():
    """
    ↳ PrekeyBundleMapper.to_schema: mapea de PrekeyBundleEntity a ORM PrekeyBundleSchema
    """
    pk_id = uuid4()
    u_id = uuid4()
    now = datetime.now(timezone.utc)
    entity = PrekeyBundleEntity(
        id=pk_id,
        user_id=u_id,
        signed_prekey_pub="spk_pub",
        signature="spk_sig",
        is_active=True,
        created_at=now,
        expires_at=now,
    )

    schema = PrekeyBundleMapper.to_schema(entity)
    assert schema.id == pk_id
    assert schema.user_id == u_id
    assert schema.signed_prekey_pub == "spk_pub"
    assert schema.signature == "spk_sig"
    assert schema.is_active is True
    assert schema.created_at == now
    assert schema.expires_at == now
