from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from uuid import uuid4
import pytest

from app.modules.auth.domain.entities.user_entity import UserEntity


def test_user_entity_creation_and_attributes():
    """
    ↳ UserEntity: almacena identidad y atributos del usuario correctamente
    """
    uid = uuid4()
    now = datetime.now(timezone.utc)
    user = UserEntity(
        id=uid,
        username="alice",
        display_name="Alice",
        password_hash="argon2_hash",
        identity_sign_pub="sign_pub",
        identity_dh_pub="dh_pub",
        identity_dh_sig="dh_sig",
        created_at=now,
        updated_at=now,
    )
    assert user.id == uid
    assert user.username == "alice"
    assert user.display_name == "Alice"
    assert user.password_hash == "argon2_hash"
    assert user.identity_sign_pub == "sign_pub"
    assert user.identity_dh_pub == "dh_pub"
    assert user.identity_dh_sig == "dh_sig"
    assert user.created_at == now
    assert user.updated_at == now


def test_user_entity_create_factory():
    """
    ↳ UserEntity: metodo fabrica create inicializa id, timestamps y limpia display_name
    """
    user = UserEntity.create(
        username="alice",
        display_name="  Alice Wonderland  ",
        password_hash="hash",
        identity_sign_pub="sp",
        identity_dh_pub="dp",
        identity_dh_sig="ds",
    )
    assert user.id is not None
    assert user.username == "alice"
    assert user.display_name == "Alice Wonderland"
    assert user.created_at is not None
    assert user.updated_at == user.created_at


def test_user_entity_create_factory_fallback_display_name():
    """
    ↳ UserEntity: metodo fabrica create asigna username si display_name esta vacio
    """
    user = UserEntity.create(
        username="alice",
        display_name="   ",
        password_hash="hash",
        identity_sign_pub="sp",
        identity_dh_pub="dp",
        identity_dh_sig="ds",
    )
    assert user.display_name == "alice"


def test_user_entity_immutable():
    """
    ↳ UserEntity: es inmutable al ser frozen dataclass
    """
    user = UserEntity(
        id=uuid4(),
        username="alice",
        display_name="Alice",
        password_hash="hash",
        identity_sign_pub="sp",
        identity_dh_pub="dp",
        identity_dh_sig="ds",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    with pytest.raises(FrozenInstanceError):
        user.username = "bob"
