from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.auth.domain.value_objects.register_user_request_vo import (
    RegisterUserRequestVO,
)


class RegisterRequestDto(BaseModel):
    model_config = ConfigDict(frozen=True)

    username: str = Field(min_length=3, max_length=32)
    display_name: str = Field(default="", max_length=64)
    password: str = Field(min_length=8)
    identity_sign_pub: str = Field(min_length=1)
    identity_dh_pub: str = Field(min_length=1)
    identity_dh_sig: str = Field(min_length=1)

    def to_request(self) -> RegisterUserRequestVO:
        return RegisterUserRequestVO(
            username=self.username,
            display_name=self.display_name,
            password=self.password,
            identity_sign_pub=self.identity_sign_pub,
            identity_dh_pub=self.identity_dh_pub,
            identity_dh_sig=self.identity_dh_sig,
        )


class UserProfileResponseDto(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)

    id: UUID
    username: str
    display_name: str
    identity_sign_pub: str
    identity_dh_pub: str
    identity_dh_sig: str
    created_at: datetime
