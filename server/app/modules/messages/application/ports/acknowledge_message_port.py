from typing import Protocol
from uuid import UUID

from app.modules.messages.domain.value_objects.message_response_vo import (
    MessageResponseVO,
)


class AcknowledgeMessagePort(Protocol):
    def execute(self, current_user_id: UUID, message_id: UUID) -> MessageResponseVO:
        ...
