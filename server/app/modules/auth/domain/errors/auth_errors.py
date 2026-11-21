from app.commons.errors.base_errors import DomainError


class UserAlreadyExistsError(DomainError):
    pass


class InvalidCredentialsError(DomainError):
    pass


class SessionExpiredError(DomainError):
    pass


class RateLimitExceededError(DomainError):
    pass


class UserNotFoundError(DomainError):
    pass
