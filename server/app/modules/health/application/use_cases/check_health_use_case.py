from app.modules.health.application.ports.check_health_port import CheckHealthPort
from app.modules.health.domain.ports.database_health_port import DatabaseHealthPort
from app.modules.health.domain.rules.health_rules import HealthRules
from app.modules.health.domain.value_objects.health_status_vo import HealthStatusVO


class CheckHealthUseCase(CheckHealthPort):
    def __init__(self, db_health_port: DatabaseHealthPort) -> None:
        self._db_health_port = db_health_port

    def execute(self) -> HealthStatusVO:
        is_connected = self._db_health_port.is_database_connected()
        return HealthRules.evaluate(is_database_connected=is_connected)
