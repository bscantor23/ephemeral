from uuid import uuid4
import pytest

from app.modules.messages.domain.errors.messages_errors import (
    InvalidMessagePayloadError,
    SelfMessageNotAllowedError,
    UnauthorizedMessageAckError,
)
from app.modules.messages.domain.rules.messages_rules import MessagesRules


def test_validate_parties():
    """
    ↳ Validacion de que remitente y destinatario sean distintos
    """
    u1 = uuid4()
    u2 = uuid4()
    MessagesRules.validate_parties(u1, u2)

    with pytest.raises(SelfMessageNotAllowedError):
        MessagesRules.validate_parties(u1, u1)


def test_validate_message_payload_success():
    """
    ↳ Payload valido cumple con rangos de protocolo, msg_num y ciphertext
    """
    MessagesRules.validate_message_payload(msg_num=0, ciphertext="abc", protocol_version=1)
    MessagesRules.validate_message_payload(msg_num=10, ciphertext="a" * 1000, protocol_version=2)


def test_validate_message_payload_errors():
    """
    ↳ Errores en payload: msg_num negativo, ciphertext vacio o excesivo, protocolo < 1
    """
    with pytest.raises(InvalidMessagePayloadError, match="Message number cannot be negative"):
        MessagesRules.validate_message_payload(msg_num=-1, ciphertext="abc", protocol_version=1)

    with pytest.raises(InvalidMessagePayloadError, match="Ciphertext length must be between"):
        MessagesRules.validate_message_payload(msg_num=0, ciphertext="   ", protocol_version=1)

    with pytest.raises(InvalidMessagePayloadError, match="Ciphertext length must be between"):
        MessagesRules.validate_message_payload(msg_num=0, ciphertext="a" * 65537, protocol_version=1)

    with pytest.raises(InvalidMessagePayloadError, match="Protocol version must be greater"):
        MessagesRules.validate_message_payload(msg_num=0, ciphertext="abc", protocol_version=0)


def test_validate_ack_authorization():
    """
    ↳ Solo el destinatario del mensaje puede confirmar su recepcion
    """
    rec_id = uuid4()
    other_id = uuid4()

    MessagesRules.validate_ack_authorization(message_recipient_id=rec_id, current_user_id=rec_id)

    with pytest.raises(UnauthorizedMessageAckError):
        MessagesRules.validate_ack_authorization(message_recipient_id=rec_id, current_user_id=other_id)
