from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.modules.auth.domain.entities.user_entity import UserEntity


@dataclass(frozen=True)
class UserResponseVO:
    id: UUID
    username: str
    display_name: str
    identity_sign_pub: str
    identity_dh_pub: str
    identity_dh_sig: str
    created_at: datetime

    @classmethod
    def from_entity(cls, user: UserEntity) -> "UserResponseVO":
        return cls(
            id=user.id,
            username=user.username,
            display_name=user.display_name,
            identity_sign_pub=user.identity_sign_pub,
            identity_dh_pub=user.identity_dh_pub,
            identity_dh_sig=user.identity_dh_sig,
            created_at=user.created_at,
        )

