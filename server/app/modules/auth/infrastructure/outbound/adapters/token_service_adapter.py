from datetime import datetime, timedelta, timezone
import hashlib
import secrets

from app.modules.auth.domain.constants.auth_constants import TOKEN_BYTE_LENGTH
from app.modules.auth.domain.ports.token_service_port import TokenServicePort
from app.modules.auth.domain.value_objects.auth_token_vo import AuthTokenVO


class TokenServiceAdapter(TokenServicePort):
    def generate_token(self, ttl_minutes: int) -> AuthTokenVO:
        raw_token = secrets.token_urlsafe(TOKEN_BYTE_LENGTH)
        token_hash = self.hash_token(raw_token)
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=ttl_minutes)
        return AuthTokenVO(raw_token=raw_token, token_hash=token_hash, expires_at=expires_at)

    def hash_token(self, raw_token: str) -> str:
        return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
