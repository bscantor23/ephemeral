from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4

from app.modules.keys.domain.constants.keys_constants import PREKEY_TTL_DAYS
from app.modules.keys.domain.rules.keys_rules import KeysRules


@dataclass(frozen=True)
class PrekeyBundleEntity:
    id: UUID
    user_id: UUID
    signed_prekey_pub: str
    signature: str
    is_active: bool
    created_at: datetime
    expires_at: datetime

    @classmethod
    def create(
        cls,
        user_id: UUID,
        signed_prekey_pub: str,
        signature: str,
        ttl_days: int = PREKEY_TTL_DAYS,
    ) -> "PrekeyBundleEntity":
        now = datetime.now(timezone.utc)
        expires_at = KeysRules.calculate_expiration(now, days=ttl_days)
        return cls(
            id=uuid4(),
            user_id=user_id,
            signed_prekey_pub=signed_prekey_pub,
            signature=signature,
            is_active=True,
            created_at=now,
            expires_at=expires_at,
        )
