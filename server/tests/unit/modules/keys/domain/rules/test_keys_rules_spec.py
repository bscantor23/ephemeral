from datetime import datetime, timedelta, timezone

from app.modules.keys.domain.errors.keys_errors import PrekeyExpiredError
from app.modules.keys.domain.rules.keys_rules import KeysRules


def test_keys_rules_calculate_expiration():
    """
    ↳ KeysRules.calculate_expiration: suma exactamente el número de días a la fecha base
    """
    base = datetime(2026, 11, 22, 12, 0, 0, tzinfo=timezone.utc)
    res = KeysRules.calculate_expiration(base, days=7)
    assert res == datetime(2026, 11, 29, 12, 0, 0, tzinfo=timezone.utc)


def test_keys_rules_validate_not_expired_success():
    """
    ↳ KeysRules.validate_not_expired: no lanza excepción si la fecha es futura
    """
    future = datetime.now(timezone.utc) + timedelta(days=2)
    KeysRules.validate_not_expired(future)


def test_keys_rules_validate_not_expired_failure():
    """
    ↳ KeysRules.validate_not_expired: lanza PrekeyExpiredError si la fecha expiró
    """
    past = datetime.now(timezone.utc) - timedelta(seconds=10)
    try:
        KeysRules.validate_not_expired(past)
        assert False, "Debería haber lanzado PrekeyExpiredError"
    except PrekeyExpiredError as e:
        assert "expired" in str(e).lower()
