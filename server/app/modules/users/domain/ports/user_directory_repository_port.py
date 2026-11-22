from typing import Optional, Protocol
from uuid import UUID

from app.modules.users.domain.entities.user_profile_entity import UserProfileEntity
from app.modules.users.domain.value_objects.list_users_vo import ListUsersQueryVO


class UserDirectoryRepositoryPort(Protocol):
    def get_by_id(self, user_id: UUID) -> Optional[UserProfileEntity]:
        ...

    def get_by_username(self, username: str) -> Optional[UserProfileEntity]:
        ...

    def list_users(
        self, query: ListUsersQueryVO
    ) -> tuple[list[UserProfileEntity], int]:
        ...
