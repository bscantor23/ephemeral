from typing import Callable, Optional
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

    def save(self, bundle: PrekeyBundleEntity) -> PrekeyBundleEntity:
        session = self._session_factory()
        try:
            schema = PrekeyBundleMapper.to_schema(bundle)
            session.add(schema)
            session.commit()
            session.refresh(schema)
            return PrekeyBundleMapper.to_entity(schema)
        finally:
            session.close()

    def get_active_by_user_id(self, user_id: UUID) -> Optional[PrekeyBundleEntity]:
        session = self._session_factory()
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
            session.close()

    def deactivate_all_for_user(self, user_id: UUID) -> None:
        session = self._session_factory()
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
            session.close()
