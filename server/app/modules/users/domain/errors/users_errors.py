from app.commons.errors.base_errors import DomainError


class UserNotFoundError(DomainError):
    def __init__(self, message: str = "User not found") -> None:
        super().__init__(message)


class InvalidPaginationError(DomainError):
    def __init__(self, message: str = "Invalid pagination parameters") -> None:
        super().__init__(message)


class InvalidSearchQueryError(DomainError):
    def __init__(self, message: str = "Invalid search query") -> None:
        super().__init__(message)
