from app.commons.errors.base_errors import DomainError
from app.modules.keys.domain.errors.keys_errors import (
    NoActivePrekeyError,
    PrekeyExpiredError,
    TargetUserNotFoundError,
)


def test_keys_errors_inherit_from_domain_error():
    """
    ↳ keys_errors: todos los errores del dominio keys heredan de DomainError
    """
    err1 = TargetUserNotFoundError("User not found")
    err2 = NoActivePrekeyError("No active prekey")
    err3 = PrekeyExpiredError("Prekey has expired")

    assert isinstance(err1, DomainError)
    assert isinstance(err2, DomainError)
    assert isinstance(err3, DomainError)
    assert str(err1) == "User not found"
    assert str(err2) == "No active prekey"
    assert str(err3) == "Prekey has expired"
