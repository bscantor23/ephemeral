from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.modules.auth.application.ports.validate_token_port import (
    ValidateTokenPort,
)
from app.modules.auth.application.use_cases.validate_token_use_case import (
    ValidateTokenUseCase,
)
from app.modules.auth.domain.value_objects.user_response_vo import UserResponseVO
from app.modules.auth.infrastructure.outbound.adapters.token_service_adapter import (
    TokenServiceAdapter,
)
from app.modules.auth.infrastructure.outbound.persistence.repositories.postgres_session_repository import (
    PostgresSessionRepository,
)
from app.modules.auth.infrastructure.outbound.persistence.repositories.postgres_user_repository import (
    PostgresUserRepository,
)

security_scheme = HTTPBearer(auto_error=False)


def get_validate_token_use_case() -> ValidateTokenPort:
    session_repo = PostgresSessionRepository()
    user_repo = PostgresUserRepository()
    token_service = TokenServiceAdapter()
    return ValidateTokenUseCase(
        session_repo=session_repo,
        user_repo=user_repo,
        token_service=token_service,
    )


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    use_case: ValidateTokenPort = Depends(get_validate_token_use_case),
) -> UserResponseVO:
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return use_case.execute(raw_token=credentials.credentials)
