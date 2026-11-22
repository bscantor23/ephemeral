from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class PublicBundleResponseVO:
    user_id: UUID
    identity_sign_pub: str
    identity_dh_pub: str
    identity_dh_sig: str
    signed_prekey_id: UUID
    signed_prekey_pub: str
    signature: str
    expires_at: datetime
