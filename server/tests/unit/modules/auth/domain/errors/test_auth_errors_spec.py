import pytest

from app.commons.errors.base_errors import DomainError
from app.modules.auth.domain.errors.auth_errors import (
    InvalidCredentialsError,
    RateLimitExceededError,
    SessionExpiredError,
    UserAlreadyExistsError,
    UserNotFoundError,
)


def test_auth_errors_inherit_from_domain_error():
    """
    ↳ Errores: todas las excepciones de autenticacion heredan de DomainError
    """
    assert issubclass(UserAlreadyExistsError, DomainError)
    assert issubclass(InvalidCredentialsError, DomainError)
    assert issubclass(SessionExpiredError, DomainError)
    assert issubclass(RateLimitExceededError, DomainError)
    assert issubclass(UserNotFoundError, DomainError)


def test_auth_errors_messages():
    """
    ↳ Errores: excepciones conservan mensaje de detalle suministrado
    """
    e1 = UserAlreadyExistsError("User duplicate")
    assert str(e1) == "User duplicate"

    e2 = InvalidCredentialsError("Bad pass")
    assert str(e2) == "Bad pass"

    e3 = SessionExpiredError("Expired")
    assert str(e3) == "Expired"

    e4 = RateLimitExceededError("Too fast")
    assert str(e4) == "Too fast"

    e5 = UserNotFoundError("Missing user")
    assert str(e5) == "Missing user"
