from collections.abc import Callable, Generator
from typing import Optional
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.commons.db.schemas.prekey_bundle_schema import PrekeyBundleSchema
from app.commons.db.schemas.user_schema import UserSchema
from app.commons.db.session import get_db_session
from app.modules.users.domain.entities.user_profile_entity import UserProfileEntity
from app.modules.users.domain.ports.user_directory_repository_port import (
    UserDirectoryRepositoryPort,
)
from app.modules.users.domain.value_objects.list_users_vo import ListUsersQueryVO
from app.modules.users.infrastructure.outbound.persistence.mappers.user_profile_mapper import (
    UserProfileMapper,
)


class PostgresUserDirectoryRepository(UserDirectoryRepositoryPort):
    def __init__(
        self,
        session_factory: Callable[[], Generator[Session, None, None]] = get_db_session,
    ) -> None:
        self._session_factory = session_factory

    def get_by_id(self, user_id: UUID) -> Optional[UserProfileEntity]:
        session_gen = self._session_factory()
        session: Session = next(session_gen)
        try:
            stmt = select(UserSchema).where(UserSchema.id == user_id)
            user_schema = session.scalar(stmt)
            if user_schema is None:
                return None

            has_prekey = self._check_active_prekey(session, user_schema.id)
            return UserProfileMapper.to_entity(user_schema, has_prekey)
        finally:
            try:
                next(session_gen)
            except StopIteration:
                pass

    def get_by_username(self, username: str) -> Optional[UserProfileEntity]:
        session_gen = self._session_factory()
        session: Session = next(session_gen)
        try:
            stmt = select(UserSchema).where(UserSchema.username == username.lower())
            user_schema = session.scalar(stmt)
            if user_schema is None:
                return None

            has_prekey = self._check_active_prekey(session, user_schema.id)
            return UserProfileMapper.to_entity(user_schema, has_prekey)
        finally:
            try:
                next(session_gen)
            except StopIteration:
                pass

    def list_users(
        self, query: ListUsersQueryVO
    ) -> tuple[list[UserProfileEntity], int]:
        session_gen = self._session_factory()
        session: Session = next(session_gen)
        try:
            base_stmt = select(UserSchema)
            if query.search:
                pattern = f"%{query.search.lower()}%"
                base_stmt = base_stmt.where(
                    or_(
                        UserSchema.username.ilike(pattern),
                        UserSchema.display_name.ilike(pattern),
                    )
                )

            if query.exclude_user_id:
                base_stmt = base_stmt.where(UserSchema.id != query.exclude_user_id)

            count_stmt = select(func.count()).select_from(base_stmt.subquery())
            total = session.scalar(count_stmt) or 0

            results_stmt = (
                base_stmt.order_by(UserSchema.username.asc())
                .limit(query.limit)
                .offset(query.offset)
            )
            users = session.scalars(results_stmt).all()

            user_ids = [u.id for u in users]
            active_ids = set()
            if user_ids:
                prekey_stmt = select(PrekeyBundleSchema.user_id).where(
                    PrekeyBundleSchema.user_id.in_(user_ids),
                    PrekeyBundleSchema.is_active == True,
                    PrekeyBundleSchema.expires_at > func.now(),
                )
                active_ids = set(session.scalars(prekey_stmt).all())

            entities = [
                UserProfileMapper.to_entity(u, u.id in active_ids)
                for u in users
            ]
            return entities, total
        finally:
            try:
                next(session_gen)
            except StopIteration:
                pass

    def _check_active_prekey(self, session: Session, user_id: UUID) -> bool:
        stmt = (
            select(PrekeyBundleSchema.id)
            .where(
                PrekeyBundleSchema.user_id == user_id,
                PrekeyBundleSchema.is_active == True,
                PrekeyBundleSchema.expires_at > func.now(),
            )
            .limit(1)
        )
        return session.scalar(stmt) is not None
