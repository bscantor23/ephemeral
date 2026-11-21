from collections.abc import Callable, Generator
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.commons.db.schemas.session_schema import SessionSchema
from app.commons.db.session import get_db_session
from app.modules.auth.domain.entities.session_entity import SessionEntity
from app.modules.auth.domain.ports.session_repository_port import (
    SessionRepositoryPort,
)
from app.modules.auth.infrastructure.outbound.persistence.mappers.session_mapper import (
    SessionMapper,
)


class PostgresSessionRepository(SessionRepositoryPort):
    def __init__(
        self,
        session_factory: Callable[[], Generator[Session, None, None]] = get_db_session,
    ) -> None:
        self._session_factory = session_factory

    def save(self, session: SessionEntity) -> SessionEntity:
        session_gen = self._session_factory()
        session_db: Session = next(session_gen)
        try:
            schema = SessionMapper.to_schema(session)
            session_db.add(schema)
            session_db.commit()
            session_db.refresh(schema)
            return SessionMapper.to_entity(schema)
        finally:
            try:
                next(session_gen)
            except StopIteration:
                pass

    def get_by_token_hash(self, token_hash: str) -> Optional[SessionEntity]:
        session_gen = self._session_factory()
        session_db: Session = next(session_gen)
        try:
            stmt = select(SessionSchema).where(SessionSchema.token_hash == token_hash)
            schema = session_db.scalar(stmt)
            if schema is None:
                return None
            return SessionMapper.to_entity(schema)
        finally:
            try:
                next(session_gen)
            except StopIteration:
                pass

    def revoke(self, session_id: UUID, revoked_at: datetime) -> None:
        session_gen = self._session_factory()
        session_db: Session = next(session_gen)
        try:
            stmt = (
                update(SessionSchema)
                .where(SessionSchema.id == session_id)
                .values(revoked_at=revoked_at)
            )
            session_db.execute(stmt)
            session_db.commit()
        finally:
            try:
                next(session_gen)
            except StopIteration:
                pass
