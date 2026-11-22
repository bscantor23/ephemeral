from app.modules.auth.application.ports.login_user_port import LoginUserPort
from app.modules.auth.domain.entities.session_entity import SessionEntity
from app.modules.auth.domain.errors.auth_errors import InvalidCredentialsError
from app.modules.auth.domain.ports.password_hasher_port import (
    PasswordHasherPort,
)
from app.modules.auth.domain.ports.rate_limiter_port import RateLimiterPort
from app.modules.auth.domain.ports.session_repository_port import (
    SessionRepositoryPort,
)
from app.modules.auth.domain.ports.token_service_port import TokenServicePort
from app.modules.auth.domain.ports.user_repository_port import (
    UserRepositoryPort,
)
from app.modules.auth.domain.rules.auth_rules import AuthRules
from app.modules.auth.domain.value_objects.login_user_request_vo import (
    LoginUserRequestVO,
)
from app.modules.auth.domain.value_objects.login_user_response_vo import (
    LoginUserResponseVO,
)


class LoginUserUseCase(LoginUserPort):
    def __init__(
        self,
        user_repo: UserRepositoryPort,
        session_repo: SessionRepositoryPort,
        hasher: PasswordHasherPort,
        token_service: TokenServicePort,
        rate_limiter: RateLimiterPort,
        token_ttl_minutes: int,
    ) -> None:
        self._user_repo = user_repo
        self._session_repo = session_repo
        self._hasher = hasher
        self._token_service = token_service
        self._rate_limiter = rate_limiter
        self._token_ttl_minutes = token_ttl_minutes

    async def execute(self, request: LoginUserRequestVO) -> LoginUserResponseVO:
        normalized = AuthRules.normalize_username(request.username)
        self._rate_limiter.check_and_record(normalized)

        user = self._user_repo.get_by_username(normalized)
        if user is None:
            raise InvalidCredentialsError("Invalid username or password")

        is_valid = await self._hasher.verify_password(user.password_hash, request.password)
        if not is_valid:
            raise InvalidCredentialsError("Invalid username or password")

        self._rate_limiter.reset(normalized)

        token = self._token_service.generate_token(ttl_minutes=self._token_ttl_minutes)

        session = SessionEntity.create(
            user_id=user.id,
            token_hash=token.token_hash,
            expires_at=token.expires_at,
        )
        self._session_repo.save(session)

        return LoginUserResponseVO.of(token=token, user=user)
