from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class AuthTokenVO:
    raw_token: str
    token_hash: str
    expires_at: datetime
