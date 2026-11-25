from datetime import datetime, timezone
from uuid import uuid4
from fastapi.testclient import TestClient

from app.main import app
from app.modules.auth.domain.value_objects.user_response_vo import UserResponseVO
from app.modules.auth.infrastructure.outbound.security.auth_security import (
    get_current_user,
)
from app.modules.messages.application.ports.get_pending_messages_port import (
    GetPendingMessagesPort,
)
from app.modules.messages.domain.value_objects.message_response_vo import (
    MessageResponseVO,
)
from app.modules.messages.domain.value_objects.pending_messages_response_vo import (
    PendingMessagesResponseVO,
)
from app.modules.messages.infrastructure.inbound.http.dependencies import (
    get_pending_messages_use_case,
)
from tests.helpers.crypto_fixtures import generate_client_identity


class FakeGetPendingMessagesUseCase(GetPendingMessagesPort):
    def __init__(self, response: PendingMessagesResponseVO) -> None:
        self.response = response
        self.called_recipient_id = None
        self.called_limit = None

    def execute(self, recipient_id, limit=100) -> PendingMessagesResponseVO:
        self.called_recipient_id = recipient_id
        self.called_limit = limit
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


def test_get_pending_messages_endpoint_authenticated_success():
    """
    ↳ GET /messages/pending con token valido retorna lista de mensajes diferidos
    """
    user = _fake_auth_user()
    msg = MessageResponseVO(
        id=uuid4(),
        chat_session_id=uuid4(),
        sender_id=uuid4(),
        recipient_id=user.id,
        protocol_version=1,
        msg_num=0,
        ciphertext="offline_cipher",
        ephemeral_pub="eph",
        signed_prekey_id=None,
        delivered_at=None,
        created_at=datetime.now(timezone.utc),
    )
    fake_uc = FakeGetPendingMessagesUseCase(
        PendingMessagesResponseVO(messages=[msg], count=1)
    )

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_pending_messages_use_case] = lambda: fake_uc
    client = TestClient(app)

    try:
        res = client.get("/messages/pending?limit=25")
        assert res.status_code == 200
        body = res.json()
        assert body["count"] == 1
        assert body["messages"][0]["ciphertext"] == "offline_cipher"
        assert fake_uc.called_recipient_id == user.id
        assert fake_uc.called_limit == 25
    finally:
        app.dependency_overrides.clear()


def test_get_pending_messages_endpoint_unauthenticated():
    """
    ↳ GET /messages/pending sin token responde 401 Unauthorized
    """
    client = TestClient(app)
    res = client.get("/messages/pending")
    assert res.status_code == 401
