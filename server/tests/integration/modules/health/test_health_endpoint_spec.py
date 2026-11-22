from fastapi.testclient import TestClient

from app.main import app
from app.modules.health.application.ports.check_health_port import (
    CheckHealthPort,
)
from app.modules.health.domain.errors.health_errors import ServiceUnavailableError
from app.modules.health.domain.value_objects.health_status_vo import (
    HealthStatusVO,
)
from app.modules.health.infrastructure.inbound.http.dependencies import (
    get_check_health_use_case,
)


class FakeCheckHealthUseCase(CheckHealthPort):
    def __init__(self, healthy: bool = True) -> None:
        self.healthy = healthy

    def execute(self) -> HealthStatusVO:
        if not self.healthy:
            raise ServiceUnavailableError("Database is down")
        return HealthStatusVO(status="ok", database="ok", is_healthy=True)


def test_health_endpoint_success():
    """
    ↳ GET /health responde HTTP 200 cuando el servicio está activo
    """
    app.dependency_overrides[get_check_health_use_case] = lambda: FakeCheckHealthUseCase(
        healthy=True
    )
    client = TestClient(app)

    try:
        res = client.get("/health")
        assert res.status_code == 200
        assert res.json()["status"] == "ok"
        assert res.json()["database"] == "ok"
    finally:
        app.dependency_overrides.clear()


def test_health_endpoint_failure():
    """
    ↳ GET /health responde HTTP 503 cuando el servicio está degradado
    """
    app.dependency_overrides[get_check_health_use_case] = lambda: FakeCheckHealthUseCase(
        healthy=False
    )
    client = TestClient(app)

    try:
        res = client.get("/health")
        assert res.status_code == 503
        assert "detail" in res.json()
    finally:
        app.dependency_overrides.clear()


def test_health_endpoint_factory():
    """
    ↳ Inyector por defecto inicializa caso de uso CheckHealthPort
    """
    use_case = get_check_health_use_case()
    assert CheckHealthPort in type(use_case).__mro__
