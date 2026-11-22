from app.modules.keys.domain.constants.keys_constants import (
    PREKEY_TTL_DAYS,
)


def test_keys_constants_values():
    """
    ↳ keys_constants: PREKEY_TTL_DAYS está fijado en 7 días según especificación E1
    """
    assert PREKEY_TTL_DAYS == 7
