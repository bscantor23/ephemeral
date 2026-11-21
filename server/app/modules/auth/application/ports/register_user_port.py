from typing import Protocol

from app.modules.auth.domain.value_objects.register_user_request_vo import (
    RegisterUserRequestVO,
)
from app.modules.auth.domain.value_objects.user_response_vo import UserResponseVO


class RegisterUserPort(Protocol):
    async def execute(self, request: RegisterUserRequestVO) -> UserResponseVO:
        ...
