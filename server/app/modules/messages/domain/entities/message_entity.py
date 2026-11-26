from dataclasses import dataclass, replace
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4


@dataclass(frozen=True)
class MessageEntity:
    id: UUID
    chat_session_id: UUID
    sender_id: UUID
    recipient_id: UUID
    protocol_version: int
    msg_num: int
    ciphertext: str
    ephemeral_pub: Optional[str]
    signed_prekey_id: Optional[UUID]
    delivered_at: Optional[datetime]
    created_at: datetime

    @classmethod
    def create(
        cls,
        chat_session_id: UUID,
        sender_id: UUID,
        recipient_id: UUID,
        msg_num: int,
        ciphertext: str,
        ephemeral_pub: Optional[str] = None,
        signed_prekey_id: Optional[UUID] = None,
        protocol_version: int = 1,
    ) -> "MessageEntity":
        now = datetime.now(timezone.utc)
        return cls(
            id=uuid4(),
            chat_session_id=chat_session_id,
            sender_id=sender_id,
            recipient_id=recipient_id,
            protocol_version=protocol_version,
            msg_num=msg_num,
            ciphertext=ciphertext,
            ephemeral_pub=ephemeral_pub,
            signed_prekey_id=signed_prekey_id,
            delivered_at=None,
            created_at=now,
        )

    def mark_delivered(self, delivered_at: datetime) -> "MessageEntity":
        return replace(self, delivered_at=delivered_at)
