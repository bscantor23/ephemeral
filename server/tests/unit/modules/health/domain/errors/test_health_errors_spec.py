from app.commons.errors.base_errors import DomainError
from app.modules.health.domain.errors.health_errors import ServiceUnavailableError


def test_service_unavailable_error():
    """
    ↳ Errores: ServiceUnavailableError hereda de DomainError y preserva mensaje
    """
    err = ServiceUnavailableError("Database unreachable")
    assert isinstance(err, DomainError)
    assert str(err) == "Database unreachable"
