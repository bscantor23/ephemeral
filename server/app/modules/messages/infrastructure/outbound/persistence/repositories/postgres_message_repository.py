from collections.abc import Callable, Generator
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.commons.db.schemas.message_schema import MessageSchema
from app.commons.db.session import get_db_session
from app.modules.messages.domain.entities.message_entity import MessageEntity
from app.modules.messages.domain.ports.message_repository_port import (
    MessageRepositoryPort,
)
from app.modules.messages.infrastructure.outbound.persistence.mappers.message_mapper import (
    MessageMapper,
)


class PostgresMessageRepository(MessageRepositoryPort):
    def __init__(
        self,
        session_factory: Callable[[], Generator[Session, None, None]] = get_db_session,
    ) -> None:
        self._session_factory = session_factory

    def save(self, message: MessageEntity) -> MessageEntity:
        session_gen = self._session_factory()
        session: Session = next(session_gen)
        try:
            schema = MessageMapper.to_schema(message)
            session.add(schema)
            session.commit()
            session.refresh(schema)
            return MessageMapper.to_entity(schema)
        finally:
            try:
                next(session_gen)
            except StopIteration:
                pass

    def get_by_id(self, message_id: UUID) -> Optional[MessageEntity]:
        session_gen = self._session_factory()
        session: Session = next(session_gen)
        try:
            stmt = select(MessageSchema).where(MessageSchema.id == message_id)
            schema = session.scalar(stmt)
            if schema is None:
                return None
            return MessageMapper.to_entity(schema)
        finally:
            try:
                next(session_gen)
            except StopIteration:
                pass

    def get_pending_by_recipient(
        self, recipient_id: UUID, limit: int = 100
    ) -> list[MessageEntity]:
        session_gen = self._session_factory()
        session: Session = next(session_gen)
        try:
            stmt = (
                select(MessageSchema)
                .where(
                    MessageSchema.recipient_id == recipient_id,
                    MessageSchema.delivered_at.is_(None),
                )
                .order_by(MessageSchema.created_at.asc())
                .limit(limit)
            )
            schemas = session.scalars(stmt).all()
            return [MessageMapper.to_entity(s) for s in schemas]
        finally:
            try:
                next(session_gen)
            except StopIteration:
                pass

    def mark_delivered(
        self, message_id: UUID, delivered_at: datetime
    ) -> Optional[MessageEntity]:
        session_gen = self._session_factory()
        session: Session = next(session_gen)
        try:
            stmt = select(MessageSchema).where(MessageSchema.id == message_id)
            schema = session.scalar(stmt)
            if schema is None:
                return None
            schema.delivered_at = delivered_at
            session.commit()
            session.refresh(schema)
            return MessageMapper.to_entity(schema)
        finally:
            try:
                next(session_gen)
            except StopIteration:
                pass

    def delete_delivered_before(self, cutoff: datetime) -> int:
        session_gen = self._session_factory()
        session: Session = next(session_gen)
        try:
            stmt = delete(MessageSchema).where(
                MessageSchema.delivered_at.is_not(None),
                MessageSchema.delivered_at < cutoff,
            )
            result = session.execute(stmt)
            session.commit()
            return int(result.rowcount)
        finally:
            try:
                next(session_gen)
            except StopIteration:
                pass
