from datetime import datetime
from typing import Optional, Protocol
from uuid import UUID

from app.modules.auth.domain.entities.session_entity import SessionEntity


class SessionRepositoryPort(Protocol):
    def save(self, session: SessionEntity) -> SessionEntity:
        ...

    def get_by_token_hash(self, token_hash: str) -> Optional[SessionEntity]:
        ...

    def revoke(self, session_id: UUID, revoked_at: datetime) -> None:
        ...
