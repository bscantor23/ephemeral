import pytest

from app.commons.errors.base_errors import ApplicationError, DomainError


def test_domain_error_raised():
    """
    ↳ Errores: DomainError se puede lanzar y capturar
    """
    with pytest.raises(DomainError) as exc_info:
        raise DomainError("Domain business rule violated")
    assert "Domain business rule violated" in str(exc_info.value)
    assert isinstance(exc_info.value, Exception)


def test_application_error_raised():
    """
    ↳ Errores: ApplicationError se puede lanzar y capturar
    """
    with pytest.raises(ApplicationError) as exc_info:
        raise ApplicationError("Application orchestration failed")
    assert "Application orchestration failed" in str(exc_info.value)
    assert isinstance(exc_info.value, Exception)
