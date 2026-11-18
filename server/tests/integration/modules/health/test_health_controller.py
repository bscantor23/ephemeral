from fastapi.testclient import TestClient

from app.main import app
from app.modules.health.application.ports.check_health_port import CheckHealthPort
from app.modules.health.domain.value_objects.health_status_vo import HealthStatusVO
from app.modules.health.infrastructure.inbound.controllers.health_controller import (
    get_check_health_use_case,
)


class FakeCheckHealthUseCase(CheckHealthPort):
    def __init__(self, is_healthy: bool) -> None:
        self._is_healthy = is_healthy

    def execute(self) -> HealthStatusVO:
        if self._is_healthy:
            return HealthStatusVO(status="ok", database="ok", is_healthy=True)
        return HealthStatusVO(status="degraded", database="unavailable", is_healthy=False)


def test_endpoint_success():
    """GET /health: responde HTTP 200 cuando el servicio está activo"""
    app.dependency_overrides[get_check_health_use_case] = lambda: FakeCheckHealthUseCase(is_healthy=True)
    client = TestClient(app)

    try:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "database": "ok"}
    finally:
        app.dependency_overrides.clear()


def test_endpoint_failure():
    """GET /health: responde HTTP 503 cuando el servicio está degradado"""
    app.dependency_overrides[get_check_health_use_case] = lambda: FakeCheckHealthUseCase(is_healthy=False)
    client = TestClient(app)

    try:
        response = client.get("/health")
        assert response.status_code == 503
        assert response.json() == {"detail": {"status": "degraded", "database": "unavailable"}}
    finally:
        app.dependency_overrides.clear()
