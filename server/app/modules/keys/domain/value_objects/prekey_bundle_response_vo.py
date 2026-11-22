from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.modules.keys.domain.entities.prekey_bundle_entity import (
    PrekeyBundleEntity,
)


@dataclass(frozen=True)
class PrekeyBundleResponseVO:
    id: UUID
    user_id: UUID
    signed_prekey_pub: str
    signature: str
    is_active: bool
    created_at: datetime
    expires_at: datetime

    @classmethod
    def from_entity(cls, entity: PrekeyBundleEntity) -> "PrekeyBundleResponseVO":
        return cls(
            id=entity.id,
            user_id=entity.user_id,
            signed_prekey_pub=entity.signed_prekey_pub,
            signature=entity.signature,
            is_active=entity.is_active,
            created_at=entity.created_at,
            expires_at=entity.expires_at,
        )
