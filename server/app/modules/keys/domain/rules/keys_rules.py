from datetime import datetime, timedelta, timezone

from app.modules.keys.domain.errors.keys_errors import PrekeyExpiredError


class KeysRules:
    @staticmethod
    def calculate_expiration(base_time: datetime, days: int = 7) -> datetime:
        return base_time + timedelta(days=days)

    @staticmethod
    def validate_not_expired(expires_at: datetime) -> None:
        now = datetime.now(timezone.utc)
        if expires_at <= now:
            raise PrekeyExpiredError("The requested prekey bundle has expired")
