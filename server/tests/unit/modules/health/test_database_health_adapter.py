from unittest.mock import MagicMock
from sqlalchemy.exc import OperationalError

from app.modules.health.infrastructure.outbound.persistence.database_health_adapter import DatabaseHealthAdapter


def test_adapter_success():
    """Adaptador BD: SELECT 1 exitoso -> True"""
    mock_session = MagicMock()

    def fake_session_factory():
        yield mock_session

    adapter = DatabaseHealthAdapter(session_factory=fake_session_factory)
    assert adapter.is_database_connected() is True
    mock_session.execute.assert_called_once()


def test_adapter_failure():
    """Adaptador BD: error en query -> False"""
    mock_session = MagicMock()
    mock_session.execute.side_effect = OperationalError("connection refused", {}, None)

    def fake_session_factory():
        yield mock_session

    adapter = DatabaseHealthAdapter(session_factory=fake_session_factory)
    assert adapter.is_database_connected() is False
