from datetime import datetime, timezone
from uuid import uuid4
from fastapi.testclient import TestClient

from app.main import app
from app.modules.auth.domain.value_objects.user_response_vo import UserResponseVO
from app.modules.auth.infrastructure.outbound.security.auth_security import (
    get_current_user,
)
from app.modules.users.application.ports.get_user_by_id_port import GetUserByIdPort
from app.modules.users.domain.errors.users_errors import UserNotFoundError
from app.modules.users.domain.value_objects.user_profile_vo import UserProfileVO
from app.modules.users.infrastructure.inbound.http.dependencies import (
    get_user_by_id_use_case,
)
from tests.helpers.crypto_fixtures import generate_client_identity


class FakeGetByIdUseCase(GetUserByIdPort):
    def __init__(self, mode="ok", user_vo=None) -> None:
        self.mode = mode
        self.user_vo = user_vo
        self.called_id = None

    def execute(self, user_id):
        self.called_id = user_id
        if self.mode == "not_found":
            raise UserNotFoundError(f"User with id '{user_id}' was not found")
        return self.user_vo


def _fake_auth_user():
    keys = generate_client_identity()
    return UserResponseVO(
        id=uuid4(),
        username="current_user",
        display_name="Current User",
        identity_sign_pub=keys.identity_sign_pub,
        identity_dh_pub=keys.identity_dh_pub,
        identity_dh_sig=keys.identity_dh_sig,
        created_at=datetime.now(timezone.utc),
    )


def test_get_user_by_id_authenticated_success():
    """
    ↳ GET /users/{user_id} con token valido responde 200 y perfil
    """
    uid = uuid4()
    vo = UserProfileVO(
        id=uid,
        username="alice",
        display_name="Alice L.",
        identity_sign_pub="sig_alice",
        identity_dh_pub="dh_alice",
        has_active_prekey=False,
        created_at=datetime.now(timezone.utc),
    )
    fake_uc = FakeGetByIdUseCase(mode="ok", user_vo=vo)

    app.dependency_overrides[get_current_user] = _fake_auth_user
    app.dependency_overrides[get_user_by_id_use_case] = lambda: fake_uc
    client = TestClient(app)

    try:
        res = client.get(f"/users/{uid}")
        assert res.status_code == 200
        body = res.json()
        assert body["id"] == str(uid)
        assert body["username"] == "alice"
        assert body["has_active_prekey"] is False
    finally:
        app.dependency_overrides.clear()


def test_get_user_by_id_not_found():
    """
    ↳ GET /users/{user_id} responde 404 si el UUID no existe
    """
    fake_uc = FakeGetByIdUseCase(mode="not_found")
    missing_id = uuid4()

    app.dependency_overrides[get_current_user] = _fake_auth_user
    app.dependency_overrides[get_user_by_id_use_case] = lambda: fake_uc
    client = TestClient(app)

    try:
        res = client.get(f"/users/{missing_id}")
        assert res.status_code == 404
        assert "not found" in res.json()["detail"].lower()
    finally:
        app.dependency_overrides.clear()


def test_get_user_by_id_unauthenticated():
    """
    ↳ GET /users/{user_id} sin token responde 401 Unauthorized
    """
    client = TestClient(app)
    res = client.get(f"/users/{uuid4()}")
    assert res.status_code == 401
