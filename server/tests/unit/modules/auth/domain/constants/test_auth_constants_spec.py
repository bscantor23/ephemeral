from app.modules.auth.domain.constants.auth_constants import (
    ARGON2_MEMLIMIT,
    ARGON2_OPSLIMIT,
    RATE_LIMIT_MAX_ATTEMPTS,
    RATE_LIMIT_WINDOW_SECONDS,
    TOKEN_BYTE_LENGTH,
)


def test_auth_constants():
    """
    ↳ Constantes: valida valores predeterminados de seguridad para tokens y rate limiting
    """
    assert TOKEN_BYTE_LENGTH == 32
    assert ARGON2_OPSLIMIT == 3
    assert ARGON2_MEMLIMIT == 67108864
    assert RATE_LIMIT_WINDOW_SECONDS == 60
    assert RATE_LIMIT_MAX_ATTEMPTS == 5
