from typing import Protocol

from app.modules.auth.domain.value_objects.login_user_request_vo import (
    LoginUserRequestVO,
)
from app.modules.auth.domain.value_objects.login_user_response_vo import (
    LoginUserResponseVO,
)


class LoginUserPort(Protocol):
    async def execute(self, request: LoginUserRequestVO) -> LoginUserResponseVO:
        ...
