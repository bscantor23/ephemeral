from dataclasses import dataclass
from datetime import datetime

from app.modules.auth.domain.entities.user_entity import UserEntity
from app.modules.auth.domain.value_objects.auth_token_vo import AuthTokenVO
from app.modules.auth.domain.value_objects.user_response_vo import UserResponseVO


@dataclass(frozen=True)
class LoginUserResponseVO:
    access_token: str
    token_type: str
    expires_at: datetime
    user: UserResponseVO

    @classmethod
    def of(cls, token: AuthTokenVO, user: UserEntity) -> "LoginUserResponseVO":
        return cls(
            access_token=token.raw_token,
            token_type="bearer",
            expires_at=token.expires_at,
            user=UserResponseVO.from_entity(user),
        )

