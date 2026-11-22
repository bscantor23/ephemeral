from app.modules.health.application.ports.check_health_port import CheckHealthPort
from app.modules.health.application.use_cases.check_health_use_case import (
    CheckHealthUseCase,
)
from app.modules.health.infrastructure.outbound.persistence.repositories.postgres_health_repository import (
    PostgresHealthRepository,
)


def get_check_health_use_case() -> CheckHealthPort:
    repo = PostgresHealthRepository()
    return CheckHealthUseCase(health_repo=repo)
