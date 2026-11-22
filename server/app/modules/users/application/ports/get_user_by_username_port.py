from typing import Protocol

from app.modules.users.domain.value_objects.user_profile_vo import UserProfileVO


class GetUserByUsernamePort(Protocol):
    def execute(self, username: str) -> UserProfileVO:
        ...
