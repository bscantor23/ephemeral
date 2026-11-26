from datetime import datetime, timezone
from uuid import uuid4
from fastapi.testclient import TestClient
import pytest
from starlette.websockets import WebSocketDisconnect

from app.main import app
from app.modules.auth.application.ports.validate_token_port import ValidateTokenPort
from app.modules.auth.domain.errors.auth_errors import SessionExpiredError
from app.modules.auth.domain.value_objects.user_response_vo import UserResponseVO
from app.modules.auth.infrastructure.outbound.security.auth_security import (
    get_validate_token_use_case,
)
from app.modules.messages.infrastructure.inbound.websocket.connection_manager import (
    global_connection_manager,
)
from tests.helpers.crypto_fixtures import generate_client_identity


class FakeValidateTokenUseCase(ValidateTokenPort):
    def __init__(self, mode="ok", user=None) -> None:
        self.mode = mode
        self.user = user

    def execute(self, token: str) -> UserResponseVO:
        if self.mode == "invalid":
            raise SessionExpiredError("Token invalid")
        return self.user


def _fake_auth_user():
    keys = generate_client_identity()
    return UserResponseVO(
        id=uuid4(),
        username="alice",
        display_name="Alice",
        identity_sign_pub=keys.identity_sign_pub,
        identity_dh_pub=keys.identity_dh_pub,
        identity_dh_sig=keys.identity_dh_sig,
        created_at=datetime.now(timezone.utc),
    )


def test_websocket_connect_success_and_ping_pong():
    """
    ↳ WebSocket /ws conecta con token valido y responde ping con pong
    """
    user = _fake_auth_user()
    fake_uc = FakeValidateTokenUseCase(mode="ok", user=user)

    app.dependency_overrides[get_validate_token_use_case] = lambda: fake_uc
    client = TestClient(app)

    try:
        with client.websocket_connect(f"/ws?token=valid_token") as ws:
            assert global_connection_manager.is_user_online(user.id)
            ws.send_json({"type": "ping"})
            data = ws.receive_json()
            assert data == {"type": "pong"}

            ws.send_json({"type": "other"})

        assert not global_connection_manager.is_user_online(user.id)
    finally:
        app.dependency_overrides.clear()


def test_websocket_connect_missing_token():
    """
    ↳ WebSocket /ws cierra con 1008 Policy Violation si falta token
    """
    client = TestClient(app)
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with client.websocket_connect("/ws"):
            pass
    assert exc_info.value.code == 1008


def test_websocket_connect_invalid_token():
    """
    ↳ WebSocket /ws cierra con 1008 si el token es invalido
    """
    fake_uc = FakeValidateTokenUseCase(mode="invalid")
    app.dependency_overrides[get_validate_token_use_case] = lambda: fake_uc
    client = TestClient(app)

    try:
        with pytest.raises(WebSocketDisconnect) as exc_info:
            with client.websocket_connect("/ws?token=expired_token"):
                pass
        assert exc_info.value.code == 1008
    finally:
        app.dependency_overrides.clear()
