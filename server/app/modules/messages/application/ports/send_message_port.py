from typing import Protocol
from uuid import UUID

from app.modules.messages.domain.value_objects.message_response_vo import (
    MessageResponseVO,
)
from app.modules.messages.domain.value_objects.send_message_request_vo import (
    SendMessageRequestVO,
)


class SendMessagePort(Protocol):
    async def execute(
        self, sender_id: UUID, request: SendMessageRequestVO
    ) -> MessageResponseVO:
        ...
