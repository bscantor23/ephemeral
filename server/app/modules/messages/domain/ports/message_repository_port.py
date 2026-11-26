from datetime import datetime
from typing import Optional, Protocol
from uuid import UUID

from app.modules.messages.domain.entities.message_entity import MessageEntity


class MessageRepositoryPort(Protocol):
    def save(self, message: MessageEntity) -> MessageEntity:
        ...

    def get_by_id(self, message_id: UUID) -> Optional[MessageEntity]:
        ...

    def get_pending_by_recipient(
        self, recipient_id: UUID, limit: int = 100
    ) -> list[MessageEntity]:
        ...

    def mark_delivered(
        self, message_id: UUID, delivered_at: datetime
    ) -> Optional[MessageEntity]:
        ...

    def delete_delivered_before(self, cutoff: datetime) -> int:
        ...
