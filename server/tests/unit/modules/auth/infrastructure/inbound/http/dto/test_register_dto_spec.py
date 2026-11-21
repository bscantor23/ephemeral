from datetime import datetime, timezone
from uuid import uuid4
import pytest
from pydantic import ValidationError

from app.modules.auth.domain.value_objects.register_user_request_vo import (
    RegisterUserRequestVO,
)
from app.modules.auth.domain.value_objects.user_response_vo import UserResponseVO
from app.modules.auth.infrastructure.inbound.http.dto.register_dto import (
    RegisterRequestDto,
    UserProfileResponseDto,
)


def test_register_request_dto_to_request():
    """
    ↳ DTO: RegisterRequestDto valida campos y convierte a RegisterUserRequestVO
    """
    dto = RegisterRequestDto(
        username="valid_user",
        display_name="Valid",
        password="ValidPassword123!",
        identity_sign_pub="pub_sign_key",
        identity_dh_pub="pub_dh_key",
        identity_dh_sig="sig_key",
    )
    vo = dto.to_request()
    assert isinstance(vo, RegisterUserRequestVO)
    assert vo.username == "valid_user"
    assert vo.password == "ValidPassword123!"


def test_register_request_dto_short_username_fails():
    """
    ↳ DTO: RegisterRequestDto con username menor a 3 caracteres falla validacion
    """
    with pytest.raises(ValidationError):
        RegisterRequestDto(
            username="ab",
            password="Password123!",
            identity_sign_pub="sp",
            identity_dh_pub="dp",
            identity_dh_sig="ds",
        )


def test_register_request_dto_short_password_fails():
    """
    ↳ DTO: RegisterRequestDto con password menor a 8 caracteres falla validacion
    """
    with pytest.raises(ValidationError):
        RegisterRequestDto(
            username="valid_user",
            password="123",
            identity_sign_pub="sp",
            identity_dh_pub="dp",
            identity_dh_sig="ds",
        )


def test_user_profile_response_dto_from_attributes():
    """
    ↳ DTO: UserProfileResponseDto serializa desde UserResponseVO via from_attributes
    """
    uid = uuid4()
    now = datetime.now(timezone.utc)
    vo = UserResponseVO(
        id=uid,
        username="alice",
        display_name="Alice",
        identity_sign_pub="sp",
        identity_dh_pub="dp",
        identity_dh_sig="ds",
        created_at=now,
    )
    dto = UserProfileResponseDto.model_validate(vo)
    assert dto.id == uid
    assert dto.username == "alice"
    assert dto.created_at == now
