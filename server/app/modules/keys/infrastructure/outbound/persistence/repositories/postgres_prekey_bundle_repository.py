from collections.abc import Generator
from typing import Callable, Optional, Tuple, Any
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.commons.db.schemas.prekey_bundle_schema import PrekeyBundleSchema
from app.commons.db.session import SessionLocal
from app.modules.keys.domain.entities.prekey_bundle_entity import (
    PrekeyBundleEntity,
)
from app.modules.keys.domain.ports.prekey_bundle_repository_port import (
    PrekeyBundleRepositoryPort,
)
from app.modules.keys.infrastructure.outbound.persistence.mappers.prekey_bundle_mapper import (
    PrekeyBundleMapper,
)


class PostgresPrekeyBundleRepository(PrekeyBundleRepositoryPort):
    def __init__(
        self, session_factory: Callable[[], Session] = SessionLocal
    ) -> None:
        self._session_factory = session_factory

    def _get_session(self) -> Tuple[Optional[Generator], Session]:
        res = self._session_factory()
        if isinstance(res, Generator):
            return res, next(res)
        return None, res

    def _close_session(self, gen, session) -> None:
        if gen is not None:
            try:
                next(gen)
            except StopIteration:
                pass
        else:
            session.close()

    def save(self, bundle: PrekeyBundleEntity) -> PrekeyBundleEntity:
        gen, session = self._get_session()
        try:
            schema = PrekeyBundleMapper.to_schema(bundle)
            session.add(schema)
            session.commit()
            session.refresh(schema)
            return PrekeyBundleMapper.to_entity(schema)
        finally:
            self._close_session(gen, session)

    def get_active_by_user_id(self, user_id: UUID) -> Optional[PrekeyBundleEntity]:
        gen, session = self._get_session()
        try:
            stmt = (
                select(PrekeyBundleSchema)
                .where(
                    PrekeyBundleSchema.user_id == user_id,
                    PrekeyBundleSchema.is_active.is_(True),
                )
                .order_by(PrekeyBundleSchema.created_at.desc())
            )
            schema = session.scalar(stmt)
            if schema is None:
                return None
            return PrekeyBundleMapper.to_entity(schema)
        finally:
            self._close_session(gen, session)

    def deactivate_all_for_user(self, user_id: UUID) -> None:
        gen, session = self._get_session()
        try:
            stmt = (
                update(PrekeyBundleSchema)
                .where(
                    PrekeyBundleSchema.user_id == user_id,
                    PrekeyBundleSchema.is_active.is_(True),
                )
                .values(is_active=False)
            )
            session.execute(stmt)
            session.commit()
        finally:
            self._close_session(gen, session)
