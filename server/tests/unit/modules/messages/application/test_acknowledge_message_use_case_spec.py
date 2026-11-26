from datetime import datetime, timezone
from uuid import uuid4
import pytest

from app.modules.messages.application.use_cases.acknowledge_message_use_case import (
    AcknowledgeMessageUseCase,
)
from app.modules.messages.domain.entities.message_entity import MessageEntity
from app.modules.messages.domain.errors.messages_errors import (
    MessageNotFoundError,
    UnauthorizedMessageAckError,
)


class FakeAckRepo:
    def __init__(self, message: MessageEntity = None) -> None:
        self.message = message
        self.marked_id = None
        self.marked_at = None

    def get_by_id(self, message_id):
        if self.message and self.message.id == message_id:
            return self.message
        return None

    def mark_delivered(self, message_id, delivered_at):
        self.marked_id = message_id
        self.marked_at = delivered_at
        if self.message:
            return self.message.mark_delivered(delivered_at)
        return None

    def save(self, message):
        ...

    def get_pending_by_recipient(self, recipient_id, limit=100):
        ...


def test_acknowledge_message_success():
    """
    ↳ AcknowledgeMessageUseCase marca delivered_at si el receptor es el autorizado
    """
    recipient_id = uuid4()
    msg = MessageEntity.create(
        chat_session_id=uuid4(),
        sender_id=uuid4(),
        recipient_id=recipient_id,
        msg_num=1,
        ciphertext="payload",
    )
    repo = FakeAckRepo(message=msg)
    use_case = AcknowledgeMessageUseCase(message_repository=repo)

    result = use_case.execute(current_user_id=recipient_id, message_id=msg.id)

    assert result.delivered_at is not None
    assert repo.marked_id == msg.id


def test_acknowledge_message_already_delivered():
    """
    ↳ Mensaje ya entregado devuelve el estado sin volver a marcar
    """
    recipient_id = uuid4()
    delivered_time = datetime.now(timezone.utc)
    msg = MessageEntity.create(
        chat_session_id=uuid4(),
        sender_id=uuid4(),
        recipient_id=recipient_id,
        msg_num=1,
        ciphertext="payload",
    ).mark_delivered(delivered_time)

    repo = FakeAckRepo(message=msg)
    use_case = AcknowledgeMessageUseCase(message_repository=repo)

    result = use_case.execute(current_user_id=recipient_id, message_id=msg.id)

    assert result.delivered_at == delivered_time
    assert repo.marked_id is None


def test_acknowledge_message_not_found():
    """
    ↳ Error si el ID del mensaje no existe
    """
    repo = FakeAckRepo(message=None)
    use_case = AcknowledgeMessageUseCase(message_repository=repo)

    with pytest.raises(MessageNotFoundError):
        use_case.execute(current_user_id=uuid4(), message_id=uuid4())


def test_acknowledge_message_unauthorized():
    """
    ↳ Error si un usuario distinto al destinatario intenta hacer ACK
    """
    recipient_id = uuid4()
    attacker_id = uuid4()
    msg = MessageEntity.create(
        chat_session_id=uuid4(),
        sender_id=uuid4(),
        recipient_id=recipient_id,
        msg_num=1,
        ciphertext="payload",
    )
    repo = FakeAckRepo(message=msg)
    use_case = AcknowledgeMessageUseCase(message_repository=repo)

    with pytest.raises(UnauthorizedMessageAckError):
        use_case.execute(current_user_id=attacker_id, message_id=msg.id)
