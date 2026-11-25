from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class MessageResponseDTO(BaseModel):
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

    model_config = ConfigDict(from_attributes=True)


class PendingMessagesResponseDTO(BaseModel):
    messages: list[MessageResponseDTO]
    count: int

    model_config = ConfigDict(from_attributes=True)
