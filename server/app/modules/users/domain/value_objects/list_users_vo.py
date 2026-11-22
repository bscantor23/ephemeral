from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from app.modules.users.domain.value_objects.user_profile_vo import UserProfileVO


@dataclass(frozen=True)
class ListUsersQueryVO:
    search: Optional[str]
    limit: int
    offset: int
    exclude_user_id: Optional[UUID] = None


@dataclass(frozen=True)
class ListUsersResponseVO:
    users: list[UserProfileVO]
    total: int
    limit: int
    offset: int
