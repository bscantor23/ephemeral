from app.commons.errors.base_errors import DomainError
from app.modules.users.domain.errors.users_errors import (
    InvalidPaginationError,
    InvalidSearchQueryError,
    UserNotFoundError,
)


def test_users_errors_inheritance_and_messages():
    """
    ↳ Errores de dominio heredan de DomainError y definen mensajes
    """
    err1 = UserNotFoundError()
    assert isinstance(err1, DomainError)
    assert str(err1) == "User not found"

    err2 = InvalidPaginationError("Custom pagination error")
    assert isinstance(err2, DomainError)
    assert str(err2) == "Custom pagination error"

    err3 = InvalidSearchQueryError("Custom search error")
    assert isinstance(err3, DomainError)
    assert str(err3) == "Custom search error"
