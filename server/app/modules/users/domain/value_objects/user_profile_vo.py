from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class UserProfileVO:
    id: UUID
    username: str
    display_name: str
    identity_sign_pub: str
    identity_dh_pub: str
    has_active_prekey: bool
    created_at: datetime
