from datetime import datetime, timezone
from uuid import uuid4
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
import pytest

from app.modules.auth.application.ports.validate_token_port import (
    ValidateTokenPort,
)
from app.modules.auth.domain.value_objects.user_response_vo import UserResponseVO
from app.modules.auth.infrastructure.outbound.security.auth_security import (
    get_current_user,
    get_validate_token_use_case,
)


class FakeValidateTokenUseCase(ValidateTokenPort):
    def execute(self, raw_token: str) -> UserResponseVO:
        return UserResponseVO(
            id=uuid4(),
            username="auth_user",
            display_name="Auth User",
            identity_sign_pub="sp",
            identity_dh_pub="dp",
            identity_dh_sig="ds",
            created_at=datetime.now(timezone.utc),
        )


def test_get_current_user_authenticated():
    """
    ↳ Seguridad: get_current_user extrae token y retorna perfil de usuario autenticado
    """
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid_token_123")
    user = get_current_user(credentials=creds, use_case=FakeValidateTokenUseCase())
    assert user.username == "auth_user"


def test_get_current_user_none_credentials_raises_401():
    """
    ↳ Seguridad: get_current_user sin credenciales lanza HTTPException 401
    """
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(credentials=None, use_case=FakeValidateTokenUseCase())
    assert exc_info.value.status_code == 401


def test_get_current_user_empty_credentials_raises_401():
    """
    ↳ Seguridad: get_current_user con credenciales vacias lanza HTTPException 401
    """
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="")
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(credentials=creds, use_case=FakeValidateTokenUseCase())
    assert exc_info.value.status_code == 401


def test_get_validate_token_use_case_factory():
    """
    ↳ Seguridad: get_validate_token_use_case fabrica instancia que implementa ValidateTokenPort
    """
    uc = get_validate_token_use_case()
    assert ValidateTokenPort in type(uc).__mro__
