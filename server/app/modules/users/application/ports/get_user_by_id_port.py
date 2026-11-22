from typing import Protocol
from uuid import UUID

from app.modules.users.domain.value_objects.user_profile_vo import UserProfileVO


class GetUserByIdPort(Protocol):
    def execute(self, user_id: UUID) -> UserProfileVO:
        ...
