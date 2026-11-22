from datetime import datetime, timezone
from unittest.mock import MagicMock
from uuid import uuid4

from app.commons.db.schemas.prekey_bundle_schema import PrekeyBundleSchema
from app.modules.keys.domain.entities.prekey_bundle_entity import (
    PrekeyBundleEntity,
)
from app.modules.keys.infrastructure.outbound.persistence.repositories.postgres_prekey_bundle_repository import (
    PostgresPrekeyBundleRepository,
)


def test_postgres_prekey_repo_save():
    """
    ↳ PostgresPrekeyBundleRepository.save: persiste la entidad en la sesión y hace commit
    """
    mock_session = MagicMock()
    repo = PostgresPrekeyBundleRepository(session_factory=lambda: mock_session)

    entity = PrekeyBundleEntity.create(
        user_id=uuid4(),
        signed_prekey_pub="pub",
        signature="sig",
    )

    saved = repo.save(entity)
    assert saved.id == entity.id
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.close.assert_called_once()


def test_postgres_prekey_repo_get_active_found():
    """
    ↳ PostgresPrekeyBundleRepository.get_active_by_user_id: retorna entidad cuando existe prekey activa
    """
    mock_session = MagicMock()
    u_id = uuid4()
    schema = PrekeyBundleSchema(
        id=uuid4(),
        user_id=u_id,
        signed_prekey_pub="pub",
        signature="sig",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        expires_at=datetime.now(timezone.utc),
    )
    mock_session.scalar.return_value = schema

    repo = PostgresPrekeyBundleRepository(session_factory=lambda: mock_session)
    result = repo.get_active_by_user_id(u_id)

    assert result is not None
    assert result.user_id == u_id
    mock_session.scalar.assert_called_once()
    mock_session.close.assert_called_once()


def test_postgres_prekey_repo_get_active_none():
    """
    ↳ PostgresPrekeyBundleRepository.get_active_by_user_id: retorna None si no existe
    """
    mock_session = MagicMock()
    mock_session.scalar.return_value = None

    repo = PostgresPrekeyBundleRepository(session_factory=lambda: mock_session)
    result = repo.get_active_by_user_id(uuid4())

    assert result is None
    mock_session.close.assert_called_once()


def test_postgres_prekey_repo_deactivate_all():
    """
    ↳ PostgresPrekeyBundleRepository.deactivate_all_for_user: actualiza is_active=False para el usuario
    """
    mock_session = MagicMock()
    repo = PostgresPrekeyBundleRepository(session_factory=lambda: mock_session)
    u_id = uuid4()

    repo.deactivate_all_for_user(u_id)

    mock_session.execute.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.close.assert_called_once()
