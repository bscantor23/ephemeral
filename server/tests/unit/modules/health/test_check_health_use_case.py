from app.modules.health.application.use_cases.check_health_use_case import CheckHealthUseCase


class FakeDatabaseHealthPort:
    def __init__(self, is_connected: bool) -> None:
        self._is_connected = is_connected

    def is_database_connected(self) -> bool:
        return self._is_connected


def test_health_success():
    """Caso de uso: BD conectada -> estado OK"""
    fake_port = FakeDatabaseHealthPort(is_connected=True)
    use_case = CheckHealthUseCase(db_health_port=fake_port)

    status = use_case.execute()

    assert status.is_healthy is True
    assert status.status == "ok"
    assert status.database == "ok"


def test_health_failure():
    """Caso de uso: BD no conectada -> estado DEGRADED"""
    fake_port = FakeDatabaseHealthPort(is_connected=False)
    use_case = CheckHealthUseCase(db_health_port=fake_port)

    status = use_case.execute()

    assert status.is_healthy is False
    assert status.status == "degraded"
    assert status.database == "unavailable"
