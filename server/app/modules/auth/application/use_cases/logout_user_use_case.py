from datetime import datetime, timezone

from app.modules.auth.application.ports.logout_user_port import LogoutUserPort
from app.modules.auth.domain.ports.session_repository_port import (
    SessionRepositoryPort,
)
from app.modules.auth.domain.ports.token_service_port import TokenServicePort


class LogoutUserUseCase(LogoutUserPort):
    def __init__(
        self,
        session_repo: SessionRepositoryPort,
        token_service: TokenServicePort,
    ) -> None:
        self._session_repo = session_repo
        self._token_service = token_service

    def execute(self, raw_token: str) -> None:
        token_hash = self._token_service.hash_token(raw_token)
        session = self._session_repo.get_by_token_hash(token_hash)
        if session is not None and session.revoked_at is None:
            self._session_repo.revoke(session.id, datetime.now(timezone.utc))
