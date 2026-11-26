from datetime import datetime, timezone
from unittest.mock import MagicMock

from app.modules.messages.application.use_cases.purge_delivered_messages_use_case import (
    PurgeDeliveredMessagesUseCase,
)
from app.modules.messages.domain.ports.message_repository_port import (
    MessageRepositoryPort,
)


def test_purge_delivered_messages_use_case_default_retention():
    """
    ↳ PurgeDeliveredMessagesUseCase.execute: invoca delete_delivered_before con tiempo por defecto
    """
    mock_repo = MagicMock(spec=MessageRepositoryPort)
    mock_repo.delete_delivered_before.return_value = 5

    use_case = PurgeDeliveredMessagesUseCase(
        message_repo=mock_repo, default_retention_minutes=60
    )
    deleted = use_case.execute()

    assert deleted == 5
    mock_repo.delete_delivered_before.assert_called_once()
    called_cutoff = mock_repo.delete_delivered_before.call_args[0][0]
    now = datetime.now(timezone.utc)
    diff = (now - called_cutoff).total_seconds()
    assert 3590 <= diff <= 3610


def test_purge_delivered_messages_use_case_custom_retention():
    """
    ↳ PurgeDeliveredMessagesUseCase.execute: respeta retention_minutes explícito
    """
    mock_repo = MagicMock(spec=MessageRepositoryPort)
    mock_repo.delete_delivered_before.return_value = 2

    use_case = PurgeDeliveredMessagesUseCase(
        message_repo=mock_repo, default_retention_minutes=60
    )
    deleted = use_case.execute(retention_minutes=15)

    assert deleted == 2
    mock_repo.delete_delivered_before.assert_called_once()
    called_cutoff = mock_repo.delete_delivered_before.call_args[0][0]
    now = datetime.now(timezone.utc)
    diff = (now - called_cutoff).total_seconds()
    assert 890 <= diff <= 910
