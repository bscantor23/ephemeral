from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class SendMessageRequestDTO(BaseModel):
    recipient_id: UUID
    chat_session_id: UUID
    msg_num: int = Field(ge=0, description="Secuencia del ratchet de mensajes")
    ciphertext: str = Field(min_length=1, max_length=65536, description="Payload cifrado en AES-256-GCM")
    ephemeral_pub: Optional[str] = Field(default=None, description="Clave efímera ECDH para inicio X3DH")
    signed_prekey_id: Optional[UUID] = Field(default=None, description="ID del bundle prekey utilizado")
    protocol_version: int = Field(default=1, ge=1, description="Versión del protocolo E2EE")

    model_config = ConfigDict(from_attributes=True)
