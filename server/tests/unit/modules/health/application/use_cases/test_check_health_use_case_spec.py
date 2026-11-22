import pytest

from app.modules.health.application.ports.check_health_port import (
    CheckHealthPort,
)
from app.modules.health.application.use_cases.check_health_use_case import (
    CheckHealthUseCase,
)
from app.modules.health.domain.errors.health_errors import ServiceUnavailableError
from app.modules.health.domain.ports.health_repository_port import (
    HealthRepositoryPort,
)


class FakeHealthRepository(HealthRepositoryPort):
    def __init__(self, connected: bool = True) -> None:
        self.connected = connected

    def is_database_connected(self) -> bool:
        return self.connected


def test_health_success():
    """
    ↳ Caso de uso: BD conectada -> estado ok
    """
    use_case = CheckHealthUseCase(health_repo=FakeHealthRepository(connected=True))
    res = use_case.execute()
    assert res.status == "ok"
    assert res.database == "ok"
    assert res.is_healthy is True


def test_health_failure():
    """
    ↳ Caso de uso: BD no conectada -> lanza ServiceUnavailableError
    """
    use_case = CheckHealthUseCase(health_repo=FakeHealthRepository(connected=False))
    with pytest.raises(ServiceUnavailableError):
        use_case.execute()


def test_check_health_port_mro():
    """
    ↳ Caso de uso: CheckHealthUseCase implementa CheckHealthPort en su MRO
    """
    assert CheckHealthPort in CheckHealthUseCase.__mro__
