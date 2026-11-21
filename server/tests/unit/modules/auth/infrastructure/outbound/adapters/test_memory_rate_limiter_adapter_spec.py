import time
import pytest

from app.modules.auth.domain.errors.auth_errors import RateLimitExceededError
from app.modules.auth.domain.ports.rate_limiter_port import RateLimiterPort
from app.modules.auth.infrastructure.outbound.adapters.memory_rate_limiter_adapter import (
    MemoryRateLimiterAdapter,
)


def test_rate_limiter_allows_under_limit():
    """
    ↳ Adaptador Rate Limit: permite intentos bajo el umbral maximo
    """
    limiter = MemoryRateLimiterAdapter(max_attempts=3, window_seconds=60)
    key = "user_test_ok"

    limiter.check_and_record(key)
    limiter.check_and_record(key)
    limiter.check_and_record(key)


def test_rate_limiter_blocks_over_limit():
    """
    ↳ Adaptador Rate Limit: bloquea con RateLimitExceededError al exceder umbral
    """
    limiter = MemoryRateLimiterAdapter(max_attempts=2, window_seconds=60)
    key = "user_test_block"

    limiter.check_and_record(key)
    limiter.check_and_record(key)

    with pytest.raises(RateLimitExceededError):
        limiter.check_and_record(key)


def test_rate_limiter_reset():
    """
    ↳ Adaptador Rate Limit: reset limpia historial tras login exitoso
    """
    limiter = MemoryRateLimiterAdapter(max_attempts=2, window_seconds=60)
    key = "user_test_reset"

    limiter.check_and_record(key)
    limiter.reset(key)
    limiter.check_and_record(key)


def test_rate_limiter_window_expiration():
    """
    ↳ Adaptador Rate Limit: descartar intentos fuera de la ventana de tiempo
    """
    limiter = MemoryRateLimiterAdapter(max_attempts=1, window_seconds=0.1)
    key = "expiring_key"
    limiter.check_and_record(key)
    time.sleep(0.15)
    limiter.check_and_record(key)


def test_rate_limiter_port_mro():
    """
    ↳ Adaptador Rate Limit: MemoryRateLimiterAdapter implementa RateLimiterPort en su MRO
    """
    assert RateLimiterPort in MemoryRateLimiterAdapter.__mro__
