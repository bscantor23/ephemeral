from app.modules.users.domain.constants.users_constants import (
    DEFAULT_USERS_LIMIT,
    MAX_SEARCH_LENGTH,
    MAX_USERS_LIMIT,
    MIN_SEARCH_LENGTH,
    MIN_USERS_LIMIT,
)


def test_users_constants():
    """
    ↳ Constantes de paginación y búsqueda tienen valores coherentes
    """
    assert DEFAULT_USERS_LIMIT == 50
    assert MAX_USERS_LIMIT == 100
    assert MIN_USERS_LIMIT == 1
    assert MIN_SEARCH_LENGTH == 1
    assert MAX_SEARCH_LENGTH == 64
