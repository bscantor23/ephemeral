from datetime import datetime, timezone
from uuid import uuid4
import pytest

from app.modules.auth.domain.entities.user_entity import UserEntity
from app.modules.messages.application.use_cases.send_message_use_case import (
    SendMessageUseCase,
)
from app.modules.messages.domain.entities.message_entity import MessageEntity
from app.modules.messages.domain.errors.messages_errors import (
    RecipientNotFoundError,
    SelfMessageNotAllowedError,
)
from app.modules.messages.domain.value_objects.send_message_request_vo import (
    SendMessageRequestVO,
)


class FakeMessageRepo:
    def __init__(self) -> None:
        self.saved_entity = None

    def save(self, message: MessageEntity) -> MessageEntity:
        self.saved_entity = message
        return message

    def get_by_id(self, message_id):
        ...

    def get_pending_by_recipient(self, recipient_id, limit=100):
        ...

    def mark_delivered(self, message_id, delivered_at):
        ...


class FakeUserRepo:
    def __init__(self, exists=True) -> None:
        self.exists = exists

    def get_by_id(self, user_id):
        if not self.exists:
            return None
        now = datetime.now(timezone.utc)
        return UserEntity(
            id=user_id,
            username="bob",
            display_name="Bob",
            password_hash="h",
            identity_sign_pub="sp",
            identity_dh_pub="dp",
            identity_dh_sig="ds",
            created_at=now,
            updated_at=now,
        )

    def get_by_username(self, username):
        ...

    def save(self, user):
        ...


class FakeRealtimeNotifier:
    def __init__(self) -> None:
        self.notified_recipient_id = None
        self.notified_message = None

    async def notify_message(self, recipient_id, message) -> bool:
        self.notified_recipient_id = recipient_id
        self.notified_message = message
        return True


@pytest.mark.anyio
async def test_send_message_success():
    """
    ↳ SendMessageUseCase valida destinatario, persiste y notifica en tiempo real
    """
    sender_id = uuid4()
    recipient_id = uuid4()
    session_id = uuid4()

    message_repo = FakeMessageRepo()
    user_repo = FakeUserRepo(exists=True)
    notifier = FakeRealtimeNotifier()

    use_case = SendMessageUseCase(
        message_repository=message_repo,
        user_repository=user_repo,
        realtime_notifier=notifier,
    )

    req = SendMessageRequestVO(
        recipient_id=recipient_id,
        chat_session_id=session_id,
        msg_num=0,
        ciphertext="encrypted_gcm_payload",
        ephemeral_pub="alice_eph_pub",
    )

    resp = await use_case.execute(sender_id=sender_id, request=req)

    assert resp.sender_id == sender_id
    assert resp.recipient_id == recipient_id
    assert resp.ciphertext == "encrypted_gcm_payload"
    assert message_repo.saved_entity.ciphertext == "encrypted_gcm_payload"
    assert notifier.notified_recipient_id == recipient_id
    assert notifier.notified_message.id == resp.id


@pytest.mark.anyio
async def test_send_message_self_not_allowed():
    """
    ↳ Error si emisor y receptor son el mismo usuario
    """
    uid = uuid4()
    use_case = SendMessageUseCase(FakeMessageRepo(), FakeUserRepo(), FakeRealtimeNotifier())

    req = SendMessageRequestVO(
        recipient_id=uid,
        chat_session_id=uuid4(),
        msg_num=0,
        ciphertext="payload",
    )
    with pytest.raises(SelfMessageNotAllowedError):
        await use_case.execute(sender_id=uid, request=req)


@pytest.mark.anyio
async def test_send_message_recipient_not_found():
    """
    ↳ Error si el destinatario no existe en la base de datos
    """
    sender_id = uuid4()
    recipient_id = uuid4()
    use_case = SendMessageUseCase(
        FakeMessageRepo(), FakeUserRepo(exists=False), FakeRealtimeNotifier()
    )

    req = SendMessageRequestVO(
        recipient_id=recipient_id,
        chat_session_id=uuid4(),
        msg_num=0,
        ciphertext="payload",
    )
    with pytest.raises(RecipientNotFoundError):
        await use_case.execute(sender_id=sender_id, request=req)
