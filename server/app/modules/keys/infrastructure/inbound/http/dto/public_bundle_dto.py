from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PublicBundleResponseDto(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)

    user_id: UUID
    identity_sign_pub: str
    identity_dh_pub: str
    identity_dh_sig: str
    signed_prekey_id: UUID
    signed_prekey_pub: str
    signature: str
    expires_at: datetime
