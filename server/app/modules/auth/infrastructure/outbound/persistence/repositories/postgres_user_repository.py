from collections.abc import Callable, Generator
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.commons.db.schemas.user_schema import UserSchema
from app.commons.db.session import get_db_session
from app.modules.auth.domain.entities.user_entity import UserEntity
from app.modules.auth.domain.ports.user_repository_port import (
    UserRepositoryPort,
)
from app.modules.auth.infrastructure.outbound.persistence.mappers.user_mapper import (
    UserMapper,
)


class PostgresUserRepository(UserRepositoryPort):
    def __init__(
        self,
        session_factory: Callable[[], Generator[Session, None, None]] = get_db_session,
    ) -> None:
        self._session_factory = session_factory

    def save(self, user: UserEntity) -> UserEntity:
        session_gen = self._session_factory()
        session: Session = next(session_gen)
        try:
            schema = UserMapper.to_schema(user)
            session.add(schema)
            session.commit()
            session.refresh(schema)
            return UserMapper.to_entity(schema)
        finally:
            try:
                next(session_gen)
            except StopIteration:
                pass

    def get_by_username(self, username: str) -> Optional[UserEntity]:
        session_gen = self._session_factory()
        session: Session = next(session_gen)
        try:
            stmt = select(UserSchema).where(UserSchema.username == username.lower())
            schema = session.scalar(stmt)
            if schema is None:
                return None
            return UserMapper.to_entity(schema)
        finally:
            try:
                next(session_gen)
            except StopIteration:
                pass

    def get_by_id(self, user_id: UUID) -> Optional[UserEntity]:
        session_gen = self._session_factory()
        session: Session = next(session_gen)
        try:
            stmt = select(UserSchema).where(UserSchema.id == user_id)
            schema = session.scalar(stmt)
            if schema is None:
                return None
            return UserMapper.to_entity(schema)
        finally:
            try:
                next(session_gen)
            except StopIteration:
                pass
