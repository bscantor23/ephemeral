from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.keys.domain.value_objects.upload_prekey_request_vo import (
    UploadPrekeyRequestVO,
)


class UploadPrekeyRequestDto(BaseModel):
    model_config = ConfigDict(frozen=True)

    signed_prekey_pub: str = Field(min_length=1)
    signature: str = Field(min_length=1)

    def to_request(self) -> UploadPrekeyRequestVO:
        return UploadPrekeyRequestVO(
            signed_prekey_pub=self.signed_prekey_pub,
            signature=self.signature,
        )


class PrekeyBundleResponseDto(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)

    id: UUID
    user_id: UUID
    signed_prekey_pub: str
    signature: str
    is_active: bool
    created_at: datetime
    expires_at: datetime
