import time

from app.modules.auth.domain.constants.auth_constants import (
    RATE_LIMIT_MAX_ATTEMPTS,
    RATE_LIMIT_WINDOW_SECONDS,
)
from app.modules.auth.domain.errors.auth_errors import RateLimitExceededError
from app.modules.auth.domain.ports.rate_limiter_port import RateLimiterPort


class MemoryRateLimiterAdapter(RateLimiterPort):
    def __init__(
        self,
        max_attempts: int = RATE_LIMIT_MAX_ATTEMPTS,
        window_seconds: int = RATE_LIMIT_WINDOW_SECONDS,
    ) -> None:
        self._max_attempts = max_attempts
        self._window_seconds = window_seconds
        self._attempts: dict[str, list[float]] = {}

    def check_and_record(self, key: str) -> None:
        now = time.monotonic()
        cutoff = now - self._window_seconds
        timestamps = self._attempts.get(key, [])
        valid_timestamps = [t for t in timestamps if t > cutoff]

        if len(valid_timestamps) >= self._max_attempts:
            raise RateLimitExceededError("Too many login attempts. Please try again later.")

        valid_timestamps.append(now)
        self._attempts[key] = valid_timestamps

    def reset(self, key: str) -> None:
        self._attempts.pop(key, None)
