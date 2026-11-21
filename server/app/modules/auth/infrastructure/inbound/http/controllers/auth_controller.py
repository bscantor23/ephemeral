from typing import Optional
from fastapi import APIRouter, Depends, Response, status
from fastapi.security import HTTPAuthorizationCredentials

from app.modules.auth.application.ports.login_user_port import LoginUserPort
from app.modules.auth.application.ports.logout_user_port import LogoutUserPort
from app.modules.auth.application.ports.register_user_port import RegisterUserPort
from app.modules.auth.domain.value_objects.login_user_response_vo import (
    LoginUserResponseVO,
)
from app.modules.auth.domain.value_objects.user_response_vo import UserResponseVO
from app.modules.auth.infrastructure.inbound.http.dependencies import (
    get_current_user,
    get_login_user_use_case,
    get_logout_user_use_case,
    get_register_user_use_case,
    security_scheme,
)
from app.modules.auth.infrastructure.inbound.http.dto.login_dto import (
    AuthTokenResponseDto,
    LoginRequestDto,
)
from app.modules.auth.infrastructure.inbound.http.dto.register_dto import (
    RegisterRequestDto,
    UserProfileResponseDto,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=UserProfileResponseDto,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    dto: RegisterRequestDto,
    use_case: RegisterUserPort = Depends(get_register_user_use_case),
) -> UserResponseVO:
    return await use_case.execute(dto.to_request())


@router.post(
    "/login", response_model=AuthTokenResponseDto, status_code=status.HTTP_200_OK
)
async def login(
    dto: LoginRequestDto,
    use_case: LoginUserPort = Depends(get_login_user_use_case),
) -> LoginUserResponseVO:
    return await use_case.execute(dto.to_request())


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    use_case: LogoutUserPort = Depends(get_logout_user_use_case),
) -> Response:
    if credentials and credentials.credentials:
        use_case.execute(raw_token=credentials.credentials)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me", response_model=UserProfileResponseDto, status_code=status.HTTP_200_OK)
def get_me(current_user: UserResponseVO = Depends(get_current_user)) -> UserResponseVO:
    return current_user
