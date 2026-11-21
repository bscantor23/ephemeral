from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID, uuid4
import pytest

from app.modules.auth.application.ports.validate_token_port import (
    ValidateTokenPort,
)
from app.modules.auth.application.use_cases.validate_token_use_case import (
    ValidateTokenUseCase,
)
from app.modules.auth.domain.entities.session_entity import SessionEntity
from app.modules.auth.domain.entities.user_entity import UserEntity
from app.modules.auth.domain.errors.auth_errors import (
    InvalidCredentialsError,
    SessionExpiredError,
    UserNotFoundError,
)
from app.modules.auth.domain.value_objects.user_response_vo import UserResponseVO


class FakeTokenService:
    def hash_token(self, raw_token: str) -> str:
        return f"hash_{raw_token}"


class FakeSessionRepo:
    def __init__(self, session: Optional[SessionEntity] = None) -> None:
        self.session = session

    def get_by_token_hash(self, token_hash: str) -> Optional[SessionEntity]:
        if self.session and self.session.token_hash == token_hash:
            return self.session
        return None

    def revoke(self, session_id: UUID, revoked_at: datetime) -> None:
        if self.session:
            object.__setattr__(self.session, "revoked_at", revoked_at)


class FakeUserRepo:
    def __init__(self, user: Optional[UserEntity] = None) -> None:
        self.user = user

    def get_by_id(self, user_id: UUID) -> Optional[UserEntity]:
        if self.user and self.user.id == user_id:
            return self.user
        return None


def make_user() -> UserEntity:
    return UserEntity(
        id=uuid4(),
        username="charlie",
        display_name="Charlie",
        password_hash="pw",
        identity_sign_pub="k1",
        identity_dh_pub="k2",
        identity_dh_sig="s1",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


def test_validate_token_success():
    """
    ↳ Caso de uso: token valido y activo retorna usuario correspondiente
    """
    user = make_user()
    session = SessionEntity(
        id=uuid4(),
        user_id=user.id,
        token_hash="hash_valid_token",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=60),
        revoked_at=None,
        created_at=datetime.now(timezone.utc),
    )
    use_case = ValidateTokenUseCase(
        session_repo=FakeSessionRepo(session=session),
        user_repo=FakeUserRepo(user=user),
        token_service=FakeTokenService(),
    )

    found_user = use_case.execute("valid_token")
    assert isinstance(found_user, UserResponseVO)
    assert found_user.id == user.id


def test_validate_token_missing_session_fails():
    """
    ↳ Caso de uso: sesion inexistente lanza InvalidCredentialsError
    """
    use_case = ValidateTokenUseCase(
        session_repo=FakeSessionRepo(session=None),
        user_repo=FakeUserRepo(user=None),
        token_service=FakeTokenService(),
    )

    with pytest.raises(InvalidCredentialsError):
        use_case.execute("missing_token")


def test_validate_token_revoked_session_fails():
    """
    ↳ Caso de uso: sesion revocada lanza SessionExpiredError
    """
    user = make_user()
    session = SessionEntity(
        id=uuid4(),
        user_id=user.id,
        token_hash="hash_revoked_token",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=60),
        revoked_at=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc),
    )
    use_case = ValidateTokenUseCase(
        session_repo=FakeSessionRepo(session=session),
        user_repo=FakeUserRepo(user=user),
        token_service=FakeTokenService(),
    )

    with pytest.raises(SessionExpiredError):
        use_case.execute("revoked_token")


def test_validate_token_user_not_found_fails():
    """
    ↳ Caso de uso: usuario eliminado con sesion activa lanza UserNotFoundError
    """
    session = SessionEntity(
        id=uuid4(),
        user_id=uuid4(),
        token_hash="hash_orphan_token",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=60),
        revoked_at=None,
        created_at=datetime.now(timezone.utc),
    )
    use_case = ValidateTokenUseCase(
        session_repo=FakeSessionRepo(session=session),
        user_repo=FakeUserRepo(user=None),
        token_service=FakeTokenService(),
    )

    with pytest.raises(UserNotFoundError):
        use_case.execute("orphan_token")


def test_validate_token_use_case_port_mro():
    """
    ↳ Caso de uso: ValidateTokenUseCase implementa ValidateTokenPort en su MRO
    """
    assert ValidateTokenPort in ValidateTokenUseCase.__mro__
