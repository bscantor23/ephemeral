from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID, uuid4

from app.modules.auth.application.ports.logout_user_port import LogoutUserPort
from app.modules.auth.application.use_cases.logout_user_use_case import (
    LogoutUserUseCase,
)
from app.modules.auth.domain.entities.session_entity import SessionEntity


class FakeTokenService:
    def hash_token(self, raw_token: str) -> str:
        return f"hash_{raw_token}"


class FakeSessionRepo:
    def __init__(self, session: Optional[SessionEntity] = None) -> None:
        self.session = session
        self.revoked = False

    def get_by_token_hash(self, token_hash: str) -> Optional[SessionEntity]:
        if self.session and self.session.token_hash == token_hash:
            return self.session
        return None

    def revoke(self, session_id: UUID, revoked_at: datetime) -> None:
        self.revoked = True
        if self.session:
            object.__setattr__(self.session, "revoked_at", revoked_at)


def test_logout_revokes_active_session():
    """
    ↳ Caso de uso: logout marca sesion activa con fecha de revocacion
    """
    session = SessionEntity(
        id=uuid4(),
        user_id=uuid4(),
        token_hash="hash_my_token",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=60),
        revoked_at=None,
        created_at=datetime.now(timezone.utc),
    )
    repo = FakeSessionRepo(session=session)
    use_case = LogoutUserUseCase(session_repo=repo, token_service=FakeTokenService())

    use_case.execute("my_token")

    assert repo.revoked is True
    assert session.revoked_at is not None


def test_logout_unknown_token_succeeds_silently():
    """
    ↳ Caso de uso: logout con token inexistente no falla
    """
    repo = FakeSessionRepo(session=None)
    use_case = LogoutUserUseCase(session_repo=repo, token_service=FakeTokenService())

    use_case.execute("unknown_token")
    assert repo.revoked is False


def test_logout_user_use_case_port_mro():
    """
    ↳ Caso de uso: LogoutUserUseCase implementa LogoutUserPort en su MRO
    """
    assert LogoutUserPort in LogoutUserUseCase.__mro__
