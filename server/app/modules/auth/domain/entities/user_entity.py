from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4


@dataclass(frozen=True)
class UserEntity:
    id: UUID
    username: str
    display_name: str
    password_hash: str
    identity_sign_pub: str
    identity_dh_pub: str
    identity_dh_sig: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(
        cls,
        username: str,
        display_name: str,
        password_hash: str,
        identity_sign_pub: str,
        identity_dh_pub: str,
        identity_dh_sig: str,
    ) -> "UserEntity":
        now = datetime.now(timezone.utc)
        return cls(
            id=uuid4(),
            username=username,
            display_name=display_name.strip() or username,
            password_hash=password_hash,
            identity_sign_pub=identity_sign_pub,
            identity_dh_pub=identity_dh_pub,
            identity_dh_sig=identity_dh_sig,
            created_at=now,
            updated_at=now,
        )
