from typing import Protocol

from app.modules.auth.domain.value_objects.auth_token_vo import AuthTokenVO


class TokenServicePort(Protocol):
    def generate_token(self, ttl_minutes: int) -> AuthTokenVO:
        ...

    def hash_token(self, raw_token: str) -> str:
        ...
