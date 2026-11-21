from typing import Optional, Protocol
from uuid import UUID

from app.modules.auth.domain.entities.user_entity import UserEntity


class UserRepositoryPort(Protocol):
    def save(self, user: UserEntity) -> UserEntity:
        ...

    def get_by_username(self, username: str) -> Optional[UserEntity]:
        ...

    def get_by_id(self, user_id: UUID) -> Optional[UserEntity]:
        ...
