from typing import Any, Optional

from app.commons.errors.base_errors import DomainError


class ServiceUnavailableError(DomainError):
    def __init__(self, message: str = "Service unavailable", detail: Optional[Any] = None) -> None:
        super().__init__(message)
        self.detail = detail
