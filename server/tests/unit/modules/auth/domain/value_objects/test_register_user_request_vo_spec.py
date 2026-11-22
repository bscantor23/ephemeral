from dataclasses import FrozenInstanceError
import pytest

from app.modules.auth.domain.value_objects.register_user_request_vo import (
    RegisterUserRequestVO,
)


def test_register_user_request_vo():
    """
    ↳ RegisterUserRequestVO: inicializa y asegura inmutabilidad de los datos de registro
    """
    vo = RegisterUserRequestVO(
        username="alice",
        display_name="Alice",
        password="secretpassword",
        identity_sign_pub="sp",
        identity_dh_pub="dp",
        identity_dh_sig="ds",
    )
    assert vo.username == "alice"
    assert vo.display_name == "Alice"
    assert vo.password == "secretpassword"

    with pytest.raises(FrozenInstanceError):
        vo.username = "changed"
