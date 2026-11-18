from typing import Protocol


class DatabaseHealthPort(Protocol):
    def is_database_connected(self) -> bool:
        ...
