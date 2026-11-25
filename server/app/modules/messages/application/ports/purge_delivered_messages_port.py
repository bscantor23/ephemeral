from abc import ABC, abstractmethod
from typing import Optional


class PurgeDeliveredMessagesPort(ABC):
    @abstractmethod
    def execute(self, retention_minutes: Optional[int] = None) -> int:
        ...
