from datetime import datetime, timezone
from uuid import uuid4
from fastapi.testclient import TestClient

from app.main import app
from app.modules.auth.domain.value_objects.user_response_vo import UserResponseVO
from app.modules.auth.infrastructure.outbound.security.auth_security import (
    get_current_user,
)
from app.modules.messages.application.ports.acknowledge_message_port import (
    AcknowledgeMessagePort,
)
from app.modules.messages.domain.errors.messages_errors import (
    MessageNotFoundError,
    UnauthorizedMessageAckError,
)
from app.modules.messages.domain.value_objects.message_response_vo import (
    MessageResponseVO,
)
from app.modules.messages.infrastructure.inbound.http.dependencies import (
    get_acknowledge_message_use_case,
)
from tests.helpers.crypto_fixtures import generate_client_identity


class FakeAcknowledgeMessageUseCase(AcknowledgeMessagePort):
    def __init__(self, mode="ok", response=None) -> None:
        self.mode = mode
        self.response = response
        self.called_user_id = None
        self.called_message_id = None

    def execute(self, current_user_id, message_id) -> MessageResponseVO:
        self.called_user_id = current_user_id
        self.called_message_id = message_id
        if self.mode == "not_found":
            raise MessageNotFoundError()
        if self.mode == "unauthorized":
            raise UnauthorizedMessageAckError()
        return self.response


def _fake_auth_user():
    keys = generate_client_identity()
    return UserResponseVO(
        id=uuid4(),
        username="bob",
        display_name="Bob",
        identity_sign_pub=keys.identity_sign_pub,
        identity_dh_pub=keys.identity_dh_pub,
        identity_dh_sig=keys.identity_dh_sig,
        created_at=datetime.now(timezone.utc),
    )


def test_acknowledge_message_endpoint_success():
    """
    ↳ POST /messages/{id}/ack responde 200 y mensaje con delivered_at
    """
    user = _fake_auth_user()
    msg_id = uuid4()
    now = datetime.now(timezone.utc)
    resp = MessageResponseVO(
        id=msg_id,
        chat_session_id=uuid4(),
        sender_id=uuid4(),
        recipient_id=user.id,
        protocol_version=1,
        msg_num=0,
        ciphertext="payload",
        ephemeral_pub=None,
        signed_prekey_id=None,
        delivered_at=now,
        created_at=now,
    )
    fake_uc = FakeAcknowledgeMessageUseCase(mode="ok", response=resp)

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_acknowledge_message_use_case] = lambda: fake_uc
    client = TestClient(app)

    try:
        res = client.post(f"/messages/{msg_id}/ack")
        assert res.status_code == 200
        assert res.json()["delivered_at"] is not None
        assert fake_uc.called_message_id == msg_id
        assert fake_uc.called_user_id == user.id
    finally:
        app.dependency_overrides.clear()


def test_acknowledge_message_endpoint_not_found():
    """
    ↳ POST /messages/{id}/ack responde 404 si el mensaje no existe
    """
    user = _fake_auth_user()
    fake_uc = FakeAcknowledgeMessageUseCase(mode="not_found")

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_acknowledge_message_use_case] = lambda: fake_uc
    client = TestClient(app)

    try:
        res = client.post(f"/messages/{uuid4()}/ack")
        assert res.status_code == 404
    finally:
        app.dependency_overrides.clear()


def test_acknowledge_message_endpoint_unauthorized():
    """
    ↳ POST /messages/{id}/ack responde 403 si el usuario no es el destinatario
    """
    user = _fake_auth_user()
    fake_uc = FakeAcknowledgeMessageUseCase(mode="unauthorized")

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_acknowledge_message_use_case] = lambda: fake_uc
    client = TestClient(app)

    try:
        res = client.post(f"/messages/{uuid4()}/ack")
        assert res.status_code in (403, 400, 422)
    finally:
        app.dependency_overrides.clear()
