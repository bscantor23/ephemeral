from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from uuid import uuid4
import pytest

from app.modules.auth.domain.entities.user_entity import UserEntity
from app.modules.auth.domain.value_objects.auth_token_vo import AuthTokenVO
from app.modules.auth.domain.value_objects.login_user_response_vo import (
    LoginUserResponseVO,
)
from app.modules.auth.domain.value_objects.user_response_vo import UserResponseVO


def test_login_user_response_vo():
    """
    ↳ LoginUserResponseVO: encapsula token y perfil publico de forma inmutable
    """
    now = datetime.now(timezone.utc)
    user = UserResponseVO(
        id=uuid4(),
        username="david",
        display_name="David",
        identity_sign_pub="sp",
        identity_dh_pub="dp",
        identity_dh_sig="ds",
        created_at=now,
    )
    vo = LoginUserResponseVO(
        access_token="token_abc",
        token_type="bearer",
        expires_at=now,
        user=user,
    )
    assert vo.access_token == "token_abc"
    assert vo.token_type == "bearer"
    assert vo.user.username == "david"

    with pytest.raises(FrozenInstanceError):
        vo.access_token = "tampered"


def test_login_user_response_vo_of():
    """
    ↳ LoginUserResponseVO: of compone AuthTokenVO y UserEntity en una respuesta completa
    """
    uid = uuid4()
    now = datetime.now(timezone.utc)
    user = UserEntity(
        id=uid,
        username="david",
        display_name="David",
        password_hash="secret_hash",
        identity_sign_pub="sp",
        identity_dh_pub="dp",
        identity_dh_sig="ds",
        created_at=now,
        updated_at=now,
    )
    token = AuthTokenVO(
        raw_token="raw_tok",
        token_hash="hash_tok",
        expires_at=now,
    )
    vo = LoginUserResponseVO.of(token=token, user=user)
    assert vo.access_token == "raw_tok"
    assert vo.token_type == "bearer"
    assert vo.expires_at == now
    assert vo.user.id == uid
    assert vo.user.username == "david"
    assert not hasattr(vo.user, "password_hash")
