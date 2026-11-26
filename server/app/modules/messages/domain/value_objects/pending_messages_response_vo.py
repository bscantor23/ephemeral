from dataclasses import dataclass

from app.modules.messages.domain.value_objects.message_response_vo import (
    MessageResponseVO,
)


@dataclass(frozen=True)
class PendingMessagesResponseVO:
    messages: list[MessageResponseVO]
    count: int
