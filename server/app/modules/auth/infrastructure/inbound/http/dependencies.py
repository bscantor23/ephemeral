from app.commons.config.settings import get_settings
from app.modules.auth.application.ports.login_user_port import LoginUserPort
from app.modules.auth.application.ports.logout_user_port import LogoutUserPort
from app.modules.auth.application.ports.register_user_port import RegisterUserPort
from app.modules.auth.application.use_cases.login_user_use_case import LoginUserUseCase
from app.modules.auth.application.use_cases.logout_user_use_case import (
    LogoutUserUseCase,
)
from app.modules.auth.application.use_cases.register_user_use_case import (
    RegisterUserUseCase,
)
from app.modules.auth.infrastructure.outbound.adapters.memory_rate_limiter_adapter import (
    MemoryRateLimiterAdapter,
)
from app.modules.auth.infrastructure.outbound.adapters.pynacl_argon2_adapter import (
    PyNaClArgon2Adapter,
)
from app.modules.auth.infrastructure.outbound.adapters.token_service_adapter import (
    TokenServiceAdapter,
)
from app.modules.auth.infrastructure.outbound.persistence.repositories.postgres_session_repository import (
    PostgresSessionRepository,
)
from app.modules.auth.infrastructure.outbound.persistence.repositories.postgres_user_repository import (
    PostgresUserRepository,
)
from app.modules.auth.infrastructure.outbound.security.auth_security import (
    get_current_user,
    security_scheme,
)

rate_limiter_singleton = MemoryRateLimiterAdapter()
hasher_singleton = PyNaClArgon2Adapter(max_concurrency=get_settings().ARGON2_MAX_CONCURRENCY)


def get_register_user_use_case() -> RegisterUserPort:
    user_repo = PostgresUserRepository()
    return RegisterUserUseCase(user_repo=user_repo, hasher=hasher_singleton)


def get_login_user_use_case() -> LoginUserPort:
    user_repo = PostgresUserRepository()
    session_repo = PostgresSessionRepository()
    token_service = TokenServiceAdapter()
    settings = get_settings()
    return LoginUserUseCase(
        user_repo=user_repo,
        session_repo=session_repo,
        hasher=hasher_singleton,
        token_service=token_service,
        rate_limiter=rate_limiter_singleton,
        token_ttl_minutes=settings.TOKEN_TTL_MINUTES,
    )


def get_logout_user_use_case() -> LogoutUserPort:
    session_repo = PostgresSessionRepository()
    token_service = TokenServiceAdapter()
    return LogoutUserUseCase(session_repo=session_repo, token_service=token_service)
