from typing import Protocol


class HealthRepositoryPort(Protocol):
    def is_database_connected(self) -> bool:
        ...
