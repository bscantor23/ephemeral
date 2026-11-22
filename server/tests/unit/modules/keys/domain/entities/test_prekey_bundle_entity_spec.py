from datetime import datetime, timezone
from uuid import uuid4

from app.modules.keys.domain.entities.prekey_bundle_entity import (
    PrekeyBundleEntity,
)


def test_prekey_bundle_entity_creation():
    """
    ↳ PrekeyBundleEntity: creación manual con todos los campos esperados
    """
    pk_id = uuid4()
    user_id = uuid4()
    now = datetime.now(timezone.utc)
    expires = datetime.now(timezone.utc)

    entity = PrekeyBundleEntity(
        id=pk_id,
        user_id=user_id,
        signed_prekey_pub="sample_pub",
        signature="sample_sig",
        is_active=True,
        created_at=now,
        expires_at=expires,
    )

    assert entity.id == pk_id
    assert entity.user_id == user_id
    assert entity.signed_prekey_pub == "sample_pub"
    assert entity.signature == "sample_sig"
    assert entity.is_active is True
    assert entity.created_at == now
    assert entity.expires_at == expires


def test_prekey_bundle_entity_factory_create():
    """
    ↳ PrekeyBundleEntity.create: método de fábrica asigna id, fechas y estado activo
    """
    user_id = uuid4()
    entity = PrekeyBundleEntity.create(
        user_id=user_id,
        signed_prekey_pub="sample_pub_p256",
        signature="sample_sig_ecdsa",
        ttl_days=7,
    )

    assert entity.id is not None
    assert entity.user_id == user_id
    assert entity.signed_prekey_pub == "sample_pub_p256"
    assert entity.signature == "sample_sig_ecdsa"
    assert entity.is_active is True
    assert entity.created_at is not None
    assert entity.expires_at > entity.created_at
    diff_days = (entity.expires_at - entity.created_at).total_seconds() / 86400
    assert round(diff_days) == 7
