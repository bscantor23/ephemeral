from unittest.mock import MagicMock
from sqlalchemy.exc import OperationalError

from app.modules.health.domain.ports.health_repository_port import (
    HealthRepositoryPort,
)
from app.modules.health.infrastructure.outbound.persistence.repositories.postgres_health_repository import (
    PostgresHealthRepository,
)


def test_postgres_health_repo_success():
    """
    ↳ Repositorio BD: SELECT 1 exitoso -> True
    """
    mock_session = MagicMock()

    def fake_factory():
        yield mock_session

    repo = PostgresHealthRepository(session_factory=fake_factory)
    assert repo.is_database_connected() is True


def test_postgres_health_repo_failure():
    """
    ↳ Repositorio BD: error en query -> False
    """
    mock_session = MagicMock()
    mock_session.execute.side_effect = OperationalError("statement", {}, Exception("refused"))

    def fake_factory():
        yield mock_session

    repo = PostgresHealthRepository(session_factory=fake_factory)
    assert repo.is_database_connected() is False


def test_postgres_health_repo_port_mro():
    """
    ↳ Repositorio BD: PostgresHealthRepository implementa HealthRepositoryPort en su MRO
    """
    assert HealthRepositoryPort in PostgresHealthRepository.__mro__
