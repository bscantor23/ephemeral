from app.commons.errors.base_errors import DomainError


class MessageNotFoundError(DomainError):
    def __init__(self, message: str = "Message not found") -> None:
        super().__init__(message)


class RecipientNotFoundError(DomainError):
    def __init__(self, message: str = "Recipient user was not found") -> None:
        super().__init__(message)


class SelfMessageNotAllowedError(DomainError):
    def __init__(self, message: str = "Sender and recipient cannot be the same user") -> None:
        super().__init__(message)


class UnauthorizedMessageAckError(DomainError):
    def __init__(self, message: str = "Only the recipient can acknowledge message delivery") -> None:
        super().__init__(message)


class InvalidMessagePayloadError(DomainError):
    def __init__(self, message: str = "Invalid message payload parameters") -> None:
        super().__init__(message)
