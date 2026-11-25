from typing import Protocol
from uuid import UUID

from app.modules.messages.domain.value_objects.pending_messages_response_vo import (
    PendingMessagesResponseVO,
)


class GetPendingMessagesPort(Protocol):
    def execute(
        self, recipient_id: UUID, limit: int = 100
    ) -> PendingMessagesResponseVO:
        ...
