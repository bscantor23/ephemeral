from datetime import datetime, timedelta, timezone
from typing import Optional

from app.modules.messages.application.ports.purge_delivered_messages_port import (
    PurgeDeliveredMessagesPort,
)
from app.modules.messages.domain.ports.message_repository_port import (
    MessageRepositoryPort,
)


class PurgeDeliveredMessagesUseCase(PurgeDeliveredMessagesPort):
    def __init__(
        self,
        message_repo: MessageRepositoryPort,
        default_retention_minutes: int = 60,
    ) -> None:
        self._message_repo = message_repo
        self._default_retention_minutes = default_retention_minutes

    def execute(self, retention_minutes: Optional[int] = None) -> int:
        minutes = (
            retention_minutes
            if retention_minutes is not None
            else self._default_retention_minutes
        )
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=minutes)
        return self._message_repo.delete_delivered_before(cutoff)
