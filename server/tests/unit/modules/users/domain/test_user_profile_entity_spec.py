from datetime import datetime, timezone
from uuid import uuid4

from app.modules.users.domain.entities.user_profile_entity import UserProfileEntity


def test_user_profile_entity_creation():
    """
    ↳ UserProfileEntity se crea con campos inmutables
    """
    uid = uuid4()
    now = datetime.now(timezone.utc)
    entity = UserProfileEntity(
        id=uid,
        username="alice",
        display_name="Alice L.",
        identity_sign_pub="sign_pub_key",
        identity_dh_pub="dh_pub_key",
        has_active_prekey=True,
        created_at=now,
    )

    assert entity.id == uid
    assert entity.username == "alice"
    assert entity.display_name == "Alice L."
    assert entity.identity_sign_pub == "sign_pub_key"
    assert entity.identity_dh_pub == "dh_pub_key"
    assert entity.has_active_prekey is True
    assert entity.created_at == now
