from datetime import datetime, timezone
from unittest.mock import MagicMock
from uuid import uuid4

from app.commons.db.schemas.session_schema import SessionSchema
from app.modules.auth.domain.entities.session_entity import SessionEntity
from app.modules.auth.domain.ports.session_repository_port import (
    SessionRepositoryPort,
)
from app.modules.auth.infrastructure.outbound.persistence.repositories.postgres_session_repository import (
    PostgresSessionRepository,
)


def test_postgres_session_repo_save():
    """
    ↳ Repositorio Postgres: guarda sesion y confirma transaccion
    """
    mock_session = MagicMock()
    mock_schema = SessionSchema(
        id=uuid4(),
        user_id=uuid4(),
        token_hash="hash_123",
        expires_at=datetime.now(timezone.utc),
        revoked_at=None,
        created_at=datetime.now(timezone.utc),
    )

    def fake_factory():
        yield mock_session

    repo = PostgresSessionRepository(session_factory=fake_factory)
    entity = SessionEntity(
        id=mock_schema.id,
        user_id=mock_schema.user_id,
        token_hash="hash_123",
        expires_at=mock_schema.expires_at,
        revoked_at=None,
        created_at=mock_schema.created_at,
    )
    saved = repo.save(entity)
    assert saved.token_hash == "hash_123"
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()


def test_postgres_session_repo_get_by_token_hash():
    """
    ↳ Repositorio Postgres: consulta sesion por token hash o retorna None
    """
    mock_session = MagicMock()
    mock_schema = SessionSchema(
        id=uuid4(),
        user_id=uuid4(),
        token_hash="hash_target",
        expires_at=datetime.now(timezone.utc),
        revoked_at=None,
        created_at=datetime.now(timezone.utc),
    )

    def fake_factory():
        yield mock_session

    repo = PostgresSessionRepository(session_factory=fake_factory)

    mock_session.scalar.return_value = mock_schema
    found = repo.get_by_token_hash("hash_target")
    assert found is not None
    assert found.token_hash == "hash_target"

    mock_session.scalar.return_value = None
    not_found = repo.get_by_token_hash("missing_hash")
    assert not_found is None


def test_postgres_session_repo_revoke():
    """
    ↳ Repositorio Postgres: revoca sesion actualizando revoked_at
    """
    mock_session = MagicMock()

    def fake_factory():
        yield mock_session

    repo = PostgresSessionRepository(session_factory=fake_factory)
    sid = uuid4()
    now = datetime.now(timezone.utc)
    repo.revoke(sid, now)
    mock_session.execute.assert_called_once()
    mock_session.commit.assert_called_once()


def test_postgres_session_repository_port_mro():
    """
    ↳ Repositorio Postgres: PostgresSessionRepository implementa SessionRepositoryPort en su MRO
    """
    assert SessionRepositoryPort in PostgresSessionRepository.__mro__
