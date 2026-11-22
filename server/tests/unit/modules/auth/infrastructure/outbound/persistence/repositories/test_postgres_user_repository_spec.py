from datetime import datetime, timezone
from unittest.mock import MagicMock
from uuid import uuid4

from app.commons.db.schemas.user_schema import UserSchema
from app.modules.auth.domain.entities.user_entity import UserEntity
from app.modules.auth.domain.ports.user_repository_port import (
    UserRepositoryPort,
)
from app.modules.auth.infrastructure.outbound.persistence.repositories.postgres_user_repository import (
    PostgresUserRepository,
)


def test_postgres_user_repo_save():
    """
    ↳ Repositorio Postgres: guarda entidad de usuario y confirma transaccion
    """
    mock_session = MagicMock()
    mock_schema = UserSchema(
        id=uuid4(),
        username="alice",
        display_name="Alice",
        password_hash="pw",
        identity_sign_pub="sp",
        identity_dh_pub="dp",
        identity_dh_sig="ds",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    def fake_factory():
        yield mock_session

    repo = PostgresUserRepository(session_factory=fake_factory)
    entity = UserEntity(
        id=mock_schema.id,
        username="alice",
        display_name="Alice",
        password_hash="pw",
        identity_sign_pub="sp",
        identity_dh_pub="dp",
        identity_dh_sig="ds",
        created_at=mock_schema.created_at,
        updated_at=mock_schema.updated_at,
    )
    saved = repo.save(entity)
    assert saved.username == "alice"
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()


def test_postgres_user_repo_get_by_username():
    """
    ↳ Repositorio Postgres: consulta usuario por username sensible a minusculas o None si no existe
    """
    mock_session = MagicMock()
    mock_schema = UserSchema(
        id=uuid4(),
        username="alice",
        display_name="Alice",
        password_hash="pw",
        identity_sign_pub="sp",
        identity_dh_pub="dp",
        identity_dh_sig="ds",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    def fake_factory():
        yield mock_session

    repo = PostgresUserRepository(session_factory=fake_factory)

    mock_session.scalar.return_value = mock_schema
    found = repo.get_by_username("Alice")
    assert found is not None
    assert found.username == "alice"

    mock_session.scalar.return_value = None
    not_found = repo.get_by_username("missing")
    assert not_found is None


def test_postgres_user_repo_get_by_id():
    """
    ↳ Repositorio Postgres: consulta usuario por UUID o retorna None si no existe
    """
    mock_session = MagicMock()
    uid = uuid4()
    mock_schema = UserSchema(
        id=uid,
        username="alice",
        display_name="Alice",
        password_hash="pw",
        identity_sign_pub="sp",
        identity_dh_pub="dp",
        identity_dh_sig="ds",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    def fake_factory():
        yield mock_session

    repo = PostgresUserRepository(session_factory=fake_factory)

    mock_session.scalar.return_value = mock_schema
    found = repo.get_by_id(uid)
    assert found is not None
    assert found.id == uid

    mock_session.scalar.return_value = None
    not_found = repo.get_by_id(uuid4())
    assert not_found is None


def test_postgres_user_repository_port_mro():
    """
    ↳ Repositorio Postgres: PostgresUserRepository implementa UserRepositoryPort en su MRO
    """
    assert UserRepositoryPort in PostgresUserRepository.__mro__
