from app.modules.messages.domain.constants.messages_constants import (
    DEFAULT_PENDING_LIMIT,
    DEFAULT_PROTOCOL_VERSION,
    MAX_CIPHERTEXT_LENGTH,
    MIN_CIPHERTEXT_LENGTH,
    MIN_MSG_NUM,
)


def test_messages_constants():
    """
    ↳ Constantes de mensajes tienen valores coherentes
    """
    assert DEFAULT_PROTOCOL_VERSION == 1
    assert MIN_MSG_NUM == 0
    assert MAX_CIPHERTEXT_LENGTH == 65536
    assert MIN_CIPHERTEXT_LENGTH == 1
    assert DEFAULT_PENDING_LIMIT == 100
