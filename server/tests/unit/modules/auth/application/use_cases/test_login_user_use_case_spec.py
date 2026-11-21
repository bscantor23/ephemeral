from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4
import pytest

from app.modules.auth.application.ports.login_user_port import LoginUserPort
from app.modules.auth.application.use_cases.login_user_use_case import LoginUserUseCase
from app.modules.auth.domain.entities.session_entity import SessionEntity
from app.modules.auth.domain.entities.user_entity import UserEntity
from app.modules.auth.domain.errors.auth_errors import (
    InvalidCredentialsError,
    RateLimitExceededError,
)
from app.modules.auth.domain.value_objects.auth_token_vo import AuthTokenVO
from app.modules.auth.domain.value_objects.login_user_request_vo import (
    LoginUserRequestVO,
)
from app.modules.auth.domain.value_objects.login_user_response_vo import (
    LoginUserResponseVO,
)


class FakeUserRepository:
    def __init__(self, user: Optional[UserEntity] = None) -> None:
        self.user = user

    def get_by_username(self, username: str) -> Optional[UserEntity]:
        if self.user and self.user.username == username.lower():
            return self.user
        return None

    def get_by_id(self, user_id: UUID) -> Optional[UserEntity]:
        if self.user and self.user.id == user_id:
            return self.user
        return None

    def save(self, user: UserEntity) -> UserEntity:
        self.user = user
        return user


class FakeSessionRepository:
    def __init__(self) -> None:
        self.sessions: dict[str, SessionEntity] = {}

    def save(self, session: SessionEntity) -> SessionEntity:
        self.sessions[session.token_hash] = session
        return session

    def get_by_token_hash(self, token_hash: str) -> Optional[SessionEntity]:
        return self.sessions.get(token_hash)

    def revoke(self, session_id: UUID, revoked_at: datetime) -> None:
        for s in self.sessions.values():
            if s.id == session_id:
                object.__setattr__(s, "revoked_at", revoked_at)


class FakeHasher:
    async def hash_password(self, password: str) -> str:
        return f"hash_{password}"

    async def verify_password(self, password_hash: str, password: str) -> bool:
        return password_hash == f"hash_{password}"


class FakeTokenService:
    def generate_token(self, ttl_minutes: int) -> AuthTokenVO:
        return AuthTokenVO(
            raw_token="raw_secret_token",
            token_hash="sha256_hash",
            expires_at=datetime.now(timezone.utc),
        )

    def hash_token(self, raw_token: str) -> str:
        return f"hash_{raw_token}"


class FakeRateLimiter:
    def __init__(self, should_fail: bool = False) -> None:
        self.should_fail = should_fail
        self.reset_called = False

    def check_and_record(self, key: str) -> None:
        if self.should_fail:
            raise RateLimitExceededError("Rate limit exceeded")

    def reset(self, key: str) -> None:
        self.reset_called = True


def make_user() -> UserEntity:
    return UserEntity(
        id=uuid4(),
        username="bob",
        display_name="Bob",
        password_hash="hash_correctpassword",
        identity_sign_pub="k1",
        identity_dh_pub="k2",
        identity_dh_sig="s1",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.mark.anyio
async def test_login_success():
    """
    ↳ Caso de uso: login exitoso retorna usuario y token de sesion
    """
    user = make_user()
    user_repo = FakeUserRepository(user=user)
    session_repo = FakeSessionRepository()
    limiter = FakeRateLimiter()

    use_case = LoginUserUseCase(
        user_repo=user_repo,
        session_repo=session_repo,
        hasher=FakeHasher(),
        token_service=FakeTokenService(),
        rate_limiter=limiter,
        token_ttl_minutes=60,
    )

    result = await use_case.execute(LoginUserRequestVO(username="bob", password="correctpassword"))

    assert isinstance(result, LoginUserResponseVO)
    assert result.user.id == user.id
    assert result.access_token == "raw_secret_token"
    assert result.token_type == "bearer"
    assert limiter.reset_called is True
    assert "sha256_hash" in session_repo.sessions


@pytest.mark.anyio
async def test_login_wrong_username_fails():
    """
    ↳ Caso de uso: usuario inexistente lanza InvalidCredentialsError
    """
    use_case = LoginUserUseCase(
        user_repo=FakeUserRepository(user=None),
        session_repo=FakeSessionRepository(),
        hasher=FakeHasher(),
        token_service=FakeTokenService(),
        rate_limiter=FakeRateLimiter(),
        token_ttl_minutes=60,
    )

    with pytest.raises(InvalidCredentialsError):
        await use_case.execute(LoginUserRequestVO(username="unknown", password="password"))


@pytest.mark.anyio
async def test_login_wrong_password_fails():
    """
    ↳ Caso de uso: contrasena incorrecta lanza InvalidCredentialsError
    """
    user = make_user()
    use_case = LoginUserUseCase(
        user_repo=FakeUserRepository(user=user),
        session_repo=FakeSessionRepository(),
        hasher=FakeHasher(),
        token_service=FakeTokenService(),
        rate_limiter=FakeRateLimiter(),
        token_ttl_minutes=60,
    )

    with pytest.raises(InvalidCredentialsError):
        await use_case.execute(LoginUserRequestVO(username="bob", password="wrongpassword"))


@pytest.mark.anyio
async def test_login_rate_limited_fails():
    """
    ↳ Caso de uso: limite de intentos superado lanza RateLimitExceededError
    """
    use_case = LoginUserUseCase(
        user_repo=FakeUserRepository(user=make_user()),
        session_repo=FakeSessionRepository(),
        hasher=FakeHasher(),
        token_service=FakeTokenService(),
        rate_limiter=FakeRateLimiter(should_fail=True),
        token_ttl_minutes=60,
    )

    with pytest.raises(RateLimitExceededError):
        await use_case.execute(LoginUserRequestVO(username="bob", password="password"))


def test_login_user_use_case_port_mro():
    """
    ↳ Caso de uso: LoginUserUseCase implementa LoginUserPort en su MRO
    """
    assert LoginUserPort in LoginUserUseCase.__mro__
