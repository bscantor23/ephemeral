from datetime import datetime, timezone
import re

from app.commons.errors.base_errors import DomainError
from app.modules.auth.domain.entities.session_entity import SessionEntity
from app.modules.auth.domain.errors.auth_errors import SessionExpiredError

USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9_]{3,32}$")


class AuthRules:
    @staticmethod
    def normalize_username(username: str) -> str:
        cleaned = username.strip().lower()
        if not USERNAME_REGEX.match(cleaned):
            raise DomainError("Username must be 3-32 alphanumeric characters or underscores")
        return cleaned

    @staticmethod
    def validate_session_active(session: SessionEntity) -> None:
        if session.revoked_at is not None:
            raise SessionExpiredError("Session has been revoked")

        now = datetime.now(timezone.utc)
        expires_at = (
            session.expires_at
            if session.expires_at.tzinfo is not None
            else session.expires_at.replace(tzinfo=timezone.utc)
        )
        if expires_at <= now:
            raise SessionExpiredError("Session has expired")
