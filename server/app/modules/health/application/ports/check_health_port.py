from typing import Protocol

from app.modules.health.domain.value_objects.health_status_vo import HealthStatusVO


class CheckHealthPort(Protocol):
    def execute(self) -> HealthStatusVO:
        ...

