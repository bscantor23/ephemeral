from typing import Protocol

from app.modules.auth.domain.value_objects.user_response_vo import UserResponseVO


class ValidateTokenPort(Protocol):
    def execute(self, raw_token: str) -> UserResponseVO:
        ...
