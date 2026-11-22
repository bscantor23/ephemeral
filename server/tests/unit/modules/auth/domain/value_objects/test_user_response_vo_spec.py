from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from uuid import uuid4
import pytest

from app.modules.auth.domain.entities.user_entity import UserEntity
from app.modules.auth.domain.value_objects.user_response_vo import UserResponseVO


def test_user_response_vo():
    """
    ↳ UserResponseVO: representa de forma inmutable el perfil publico del usuario
    """
    uid = uuid4()
    now = datetime.now(timezone.utc)
    vo = UserResponseVO(
        id=uid,
        username="carol",
        display_name="Carol",
        identity_sign_pub="sp",
        identity_dh_pub="dp",
        identity_dh_sig="ds",
        created_at=now,
    )
    assert vo.id == uid
    assert vo.username == "carol"
    assert not hasattr(vo, "password_hash")

    with pytest.raises(FrozenInstanceError):
        vo.username = "new_carol"


def test_user_response_vo_from_entity():
    """
    ↳ UserResponseVO: from_entity proyecta datos publicos de UserEntity sin password_hash
    """
    uid = uuid4()
    now = datetime.now(timezone.utc)
    user = UserEntity(
        id=uid,
        username="alice",
        display_name="Alice",
        password_hash="secret_hash",
        identity_sign_pub="sp",
        identity_dh_pub="dp",
        identity_dh_sig="ds",
        created_at=now,
        updated_at=now,
    )
    vo = UserResponseVO.from_entity(user)
    assert vo.id == uid
    assert vo.username == "alice"
    assert vo.display_name == "Alice"
    assert vo.identity_sign_pub == "sp"
    assert vo.identity_dh_pub == "dp"
    assert vo.identity_dh_sig == "ds"
    assert vo.created_at == now
    assert not hasattr(vo, "password_hash")
