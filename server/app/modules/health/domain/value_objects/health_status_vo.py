from dataclasses import dataclass


@dataclass(frozen=True)
class HealthStatusVO:
    status: str
    database: str
    is_healthy: bool
