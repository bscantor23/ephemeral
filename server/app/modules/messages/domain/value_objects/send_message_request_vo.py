from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass(frozen=True)
class SendMessageRequestVO:
    recipient_id: UUID
    chat_session_id: UUID
    msg_num: int
    ciphertext: str
    ephemeral_pub: Optional[str] = None
    signed_prekey_id: Optional[UUID] = None
    protocol_version: int = 1
