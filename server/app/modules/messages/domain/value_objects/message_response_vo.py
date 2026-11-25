from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass(frozen=True)
class MessageResponseVO:
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
