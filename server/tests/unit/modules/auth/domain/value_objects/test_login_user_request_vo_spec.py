from dataclasses import FrozenInstanceError
import pytest

from app.modules.auth.domain.value_objects.login_user_request_vo import (
    LoginUserRequestVO,
)


def test_login_user_request_vo():
    """
    ↳ LoginUserRequestVO: almacena credenciales de login de forma inmutable
    """
    vo = LoginUserRequestVO(username="bob", password="password123")
    assert vo.username == "bob"
    assert vo.password == "password123"

    with pytest.raises(FrozenInstanceError):
        vo.password = "newpassword"
