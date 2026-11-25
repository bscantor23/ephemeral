from datetime import datetime, timezone
from uuid import uuid4
from fastapi.testclient import TestClient

from app.main import app
from app.modules.auth.domain.value_objects.user_response_vo import UserResponseVO
from app.modules.auth.infrastructure.outbound.security.auth_security import (
    get_current_user,
)
from app.modules.messages.application.ports.send_message_port import SendMessagePort
from app.modules.messages.domain.errors.messages_errors import (
    RecipientNotFoundError,
    SelfMessageNotAllowedError,
)
from app.modules.messages.domain.value_objects.message_response_vo import (
    MessageResponseVO,
)
from app.modules.messages.domain.value_objects.send_message_request_vo import (
    SendMessageRequestVO,
)
from app.modules.messages.infrastructure.inbound.http.dependencies import (
    get_send_message_use_case,
)
from tests.helpers.crypto_fixtures import generate_client_identity


class FakeSendMessageUseCase(SendMessagePort):
    def __init__(self, mode="ok", response=None) -> None:
        self.mode = mode
        self.response = response
        self.called_sender_id = None
        self.called_request = None

    async def execute(
        self, sender_id, request: SendMessageRequestVO
    ) -> MessageResponseVO:
        self.called_sender_id = sender_id
        self.called_request = request
        if self.mode == "self_not_allowed":
            raise SelfMessageNotAllowedError()
        if self.mode == "recipient_not_found":
            raise RecipientNotFoundError()
        return self.response


def _fake_auth_user(user_id=None):
    uid = user_id or uuid4()
    keys = generate_client_identity()
    return UserResponseVO(
        id=uid,
        username="alice",
        display_name="Alice",
        identity_sign_pub=keys.identity_sign_pub,
        identity_dh_pub=keys.identity_dh_pub,
        identity_dh_sig=keys.identity_dh_sig,
        created_at=datetime.now(timezone.utc),
    )


def test_send_message_endpoint_success():
    """
    ↳ POST /messages con token valido guarda mensaje y responde 201 Created
    """
    alice = _fake_auth_user()
    recipient_id = uuid4()
    session_id = uuid4()
    msg_id = uuid4()

    resp_vo = MessageResponseVO(
        id=msg_id,
        chat_session_id=session_id,
        sender_id=alice.id,
        recipient_id=recipient_id,
        protocol_version=1,
        msg_num=0,
        ciphertext="encrypted_content",
        ephemeral_pub="eph_key",
        signed_prekey_id=None,
        delivered_at=None,
        created_at=datetime.now(timezone.utc),
    )
    fake_uc = FakeSendMessageUseCase(mode="ok", response=resp_vo)

    app.dependency_overrides[get_current_user] = lambda: alice
    app.dependency_overrides[get_send_message_use_case] = lambda: fake_uc
    client = TestClient(app)

    try:
        payload = {
            "recipient_id": str(recipient_id),
            "chat_session_id": str(session_id),
            "msg_num": 0,
            "ciphertext": "encrypted_content",
            "ephemeral_pub": "eph_key",
        }
        res = client.post("/messages", json=payload)
        assert res.status_code == 201
        body = res.json()
        assert body["id"] == str(msg_id)
        assert body["ciphertext"] == "encrypted_content"
        assert fake_uc.called_sender_id == alice.id
    finally:
        app.dependency_overrides.clear()


def test_send_message_endpoint_recipient_not_found():
    """
    ↳ POST /messages responde 404 si el destinatario no existe
    """
    alice = _fake_auth_user()
    fake_uc = FakeSendMessageUseCase(mode="recipient_not_found")

    app.dependency_overrides[get_current_user] = lambda: alice
    app.dependency_overrides[get_send_message_use_case] = lambda: fake_uc
    client = TestClient(app)

    try:
        payload = {
            "recipient_id": str(uuid4()),
            "chat_session_id": str(uuid4()),
            "msg_num": 0,
            "ciphertext": "encrypted_content",
        }
        res = client.post("/messages", json=payload)
        assert res.status_code == 404
    finally:
        app.dependency_overrides.clear()


def test_send_message_endpoint_self_message():
    """
    ↳ POST /messages responde 422 si emisor y receptor coinciden
    """
    alice = _fake_auth_user()
    fake_uc = FakeSendMessageUseCase(mode="self_not_allowed")

    app.dependency_overrides[get_current_user] = lambda: alice
    app.dependency_overrides[get_send_message_use_case] = lambda: fake_uc
    client = TestClient(app)

    try:
        payload = {
            "recipient_id": str(alice.id),
            "chat_session_id": str(uuid4()),
            "msg_num": 0,
            "ciphertext": "encrypted_content",
        }
        res = client.post("/messages", json=payload)
        assert res.status_code in (400, 422)
    finally:
        app.dependency_overrides.clear()


def test_send_message_endpoint_unauthenticated():
    """
    ↳ POST /messages sin token responde 401 Unauthorized
    """
    client = TestClient(app)
    res = client.post(
        "/messages",
        json={
            "recipient_id": str(uuid4()),
            "chat_session_id": str(uuid4()),
            "msg_num": 0,
            "ciphertext": "encrypted_content",
        },
    )
    assert res.status_code == 401
