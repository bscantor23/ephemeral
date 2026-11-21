from app.modules.health.application.ports.check_health_port import CheckHealthPort
from app.modules.health.domain.errors.health_errors import ServiceUnavailableError
from app.modules.health.domain.ports.health_repository_port import (
    HealthRepositoryPort,
)
from app.modules.health.domain.rules.health_rules import HealthRules
from app.modules.health.domain.value_objects.health_status_vo import HealthStatusVO


class CheckHealthUseCase(CheckHealthPort):
    def __init__(self, health_repo: HealthRepositoryPort) -> None:
        self._health_repo = health_repo

    def execute(self) -> HealthStatusVO:
        is_connected = self._health_repo.is_database_connected()
        status = HealthRules.evaluate(is_database_connected=is_connected)
        if not status.is_healthy:
            raise ServiceUnavailableError(
                message="Service is degraded",
                detail={"status": status.status, "database": status.database},
            )
        return status
