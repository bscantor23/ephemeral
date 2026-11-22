from datetime import datetime, timezone
from uuid import uuid4

from app.modules.auth.domain.value_objects.login_user_request_vo import (
    LoginUserRequestVO,
)
from app.modules.auth.domain.value_objects.login_user_response_vo import (
    LoginUserResponseVO,
)
from app.modules.auth.domain.value_objects.user_response_vo import UserResponseVO
from app.modules.auth.infrastructure.inbound.http.dto.login_dto import (
    AuthTokenResponseDto,
    LoginRequestDto,
)


def test_login_request_dto_to_request():
    """
    ↳ DTO: LoginRequestDto convierte a LoginUserRequestVO
    """
    dto = LoginRequestDto(username="bob", password="password123")
    vo = dto.to_request()
    assert isinstance(vo, LoginUserRequestVO)
    assert vo.username == "bob"
    assert vo.password == "password123"


def test_auth_token_response_dto_from_attributes():
    """
    ↳ DTO: AuthTokenResponseDto serializa desde LoginUserResponseVO via from_attributes
    """
    now = datetime.now(timezone.utc)
    user_vo = UserResponseVO(
        id=uuid4(),
        username="bob",
        display_name="Bob",
        identity_sign_pub="sp",
        identity_dh_pub="dp",
        identity_dh_sig="ds",
        created_at=now,
    )
    login_vo = LoginUserResponseVO(
        access_token="token_123",
        token_type="bearer",
        expires_at=now,
        user=user_vo,
    )
    dto = AuthTokenResponseDto.model_validate(login_vo)
    assert dto.access_token == "token_123"
    assert dto.token_type == "bearer"
    assert dto.user.username == "bob"
