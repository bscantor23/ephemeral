from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.modules.auth.domain.value_objects.login_user_request_vo import (
    LoginUserRequestVO,
)
from app.modules.auth.infrastructure.inbound.http.dto.register_dto import (
    UserProfileResponseDto,
)


class LoginRequestDto(BaseModel):
    model_config = ConfigDict(frozen=True)

    username: str
    password: str

    def to_request(self) -> LoginUserRequestVO:
        return LoginUserRequestVO(
            username=self.username,
            password=self.password,
        )


class AuthTokenResponseDto(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)

    access_token: str
    token_type: str = "bearer"
    expires_at: datetime
    user: UserProfileResponseDto
