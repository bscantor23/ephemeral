import pytest

from app.commons.errors.base_errors import ApplicationError, DomainError


def test_domain_error_raised():
    """Errores: DomainError se puede lanzar y capturar"""
    with pytest.raises(DomainError):
        raise DomainError("domain error")


def test_application_error_raised():
    """Errores: ApplicationError se puede lanzar y capturar"""
    with pytest.raises(ApplicationError):
        raise ApplicationError("application error")
