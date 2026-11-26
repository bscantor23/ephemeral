from uuid import uuid4

from app.modules.messages.application.use_cases.get_pending_messages_use_case import (
    GetPendingMessagesUseCase,
)
from app.modules.messages.domain.entities.message_entity import MessageEntity


class FakePendingMessageRepo:
    def __init__(self, entities=None) -> None:
        self.entities = entities or []
        self.called_limit = None
        self.called_recipient_id = None

    def get_pending_by_recipient(self, recipient_id, limit=100):
        self.called_recipient_id = recipient_id
        self.called_limit = limit
        return self.entities

    def save(self, message):
        ...

    def get_by_id(self, message_id):
        ...

    def mark_delivered(self, message_id, delivered_at):
        ...


def test_get_pending_messages_use_case():
    """
    ↳ GetPendingMessagesUseCase recupera cola de mensajes diferidos no entregados
    """
    rid = uuid4()
    sid = uuid4()
    session_id = uuid4()

    e1 = MessageEntity.create(
        chat_session_id=session_id,
        sender_id=sid,
        recipient_id=rid,
        msg_num=0,
        ciphertext="m1",
    )
    e2 = MessageEntity.create(
        chat_session_id=session_id,
        sender_id=sid,
        recipient_id=rid,
        msg_num=1,
        ciphertext="m2",
    )

    repo = FakePendingMessageRepo(entities=[e1, e2])
    use_case = GetPendingMessagesUseCase(message_repository=repo)

    result = use_case.execute(recipient_id=rid, limit=50)

    assert result.count == 2
    assert len(result.messages) == 2
    assert result.messages[0].ciphertext == "m1"
    assert result.messages[1].ciphertext == "m2"
    assert repo.called_limit == 50
    assert repo.called_recipient_id == rid


def test_get_pending_messages_use_case_default_limit():
    """
    ↳ GetPendingMessagesUseCase usa limite por defecto si se pasa menor a 1
    """
    repo = FakePendingMessageRepo()
    use_case = GetPendingMessagesUseCase(message_repository=repo)
    use_case.execute(recipient_id=uuid4(), limit=-5)
    assert repo.called_limit == 100
