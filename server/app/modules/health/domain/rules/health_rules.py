from app.modules.health.domain.constants import health_constants
from app.modules.health.domain.value_objects.health_status_vo import HealthStatusVO


class HealthRules:
    @staticmethod
    def evaluate(is_database_connected: bool) -> HealthStatusVO:
        if is_database_connected:
            return HealthStatusVO(
                status=health_constants.STATUS_OK,
                database=health_constants.DATABASE_OK,
                is_healthy=True,
            )
        return HealthStatusVO(
            status=health_constants.STATUS_DEGRADED,
            database=health_constants.DATABASE_UNAVAILABLE,
            is_healthy=False,
        )
