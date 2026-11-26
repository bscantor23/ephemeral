from app.commons.errors.base_errors import DomainError
from app.modules.messages.domain.errors.messages_errors import (
    InvalidMessagePayloadError,
    MessageNotFoundError,
    RecipientNotFoundError,
    SelfMessageNotAllowedError,
    UnauthorizedMessageAckError,
)


def test_messages_errors():
    """
    ↳ Errores de dominio de mensajes heredan de DomainError
    """
    err1 = MessageNotFoundError()
    assert isinstance(err1, DomainError)
    assert str(err1) == "Message not found"

    err2 = RecipientNotFoundError()
    assert isinstance(err2, DomainError)
    assert str(err2) == "Recipient user was not found"

    err3 = SelfMessageNotAllowedError()
    assert isinstance(err3, DomainError)
    assert str(err3) == "Sender and recipient cannot be the same user"

    err4 = UnauthorizedMessageAckError()
    assert isinstance(err4, DomainError)
    assert str(err4) == "Only the recipient can acknowledge message delivery"

    err5 = InvalidMessagePayloadError("Custom payload error")
    assert isinstance(err5, DomainError)
    assert str(err5) == "Custom payload error"
