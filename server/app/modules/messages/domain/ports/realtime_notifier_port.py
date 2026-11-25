from typing import Protocol
from uuid import UUID

from app.modules.messages.domain.value_objects.message_response_vo import (
    MessageResponseVO,
)


class RealtimeNotifierPort(Protocol):
    async def notify_message(
        self, recipient_id: UUID, message: MessageResponseVO
    ) -> bool:
        ...
