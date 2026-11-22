from datetime import datetime, timezone
from uuid import uuid4
from fastapi.testclient import TestClient

from app.main import app
from app.modules.auth.domain.value_objects.user_response_vo import UserResponseVO
from app.modules.auth.infrastructure.outbound.security.auth_security import (
    get_current_user,
)
from app.modules.keys.application.ports.get_public_bundle_port import (
    GetPublicBundlePort,
)
from app.modules.keys.domain.errors.keys_errors import (
    NoActivePrekeyError,
    PrekeyExpiredError,
    TargetUserNotFoundError,
)
from app.modules.keys.domain.value_objects.public_bundle_response_vo import (
    PublicBundleResponseVO,
)
from app.modules.keys.infrastructure.inbound.http.dependencies import (
    get_public_bundle_use_case,
)
from tests.helpers.crypto_fixtures import generate_client_identity


class FakeGetBundleUseCase(GetPublicBundlePort):
    def __init__(self, mode: str = "ok") -> None:
        self.mode = mode
        self._keys = generate_client_identity()

    def execute(self, target_user_id: uuid4) -> PublicBundleResponseVO:
        if self.mode == "not_found":
            raise TargetUserNotFoundError("Target user not found")
        if self.mode == "no_active":
            raise NoActivePrekeyError("No active prekey")
        if self.mode == "expired":
            raise PrekeyExpiredError("Prekey expired")

        return PublicBundleResponseVO(
            user_id=target_user_id,
            identity_sign_pub=self._keys.identity_sign_pub,
            identity_dh_pub=self._keys.identity_dh_pub,
            identity_dh_sig=self._keys.identity_dh_sig,
            signed_prekey_id=uuid4(),
            signed_prekey_pub=self._keys.identity_dh_pub,
            signature=self._keys.identity_dh_sig,
            expires_at=datetime.now(timezone.utc),
        )


def _fake_auth_user():
    keys = generate_client_identity()
    return UserResponseVO(
        id=uuid4(),
        username="alice",
        display_name="Alice Liddell",
        identity_sign_pub=keys.identity_sign_pub,
        identity_dh_pub=keys.identity_dh_pub,
        identity_dh_sig=keys.identity_dh_sig,
        created_at=datetime.now(timezone.utc),
    )


def test_get_bundle_endpoint_success():
    """
    ↳ GET /keys/{user_id}/bundle con target valido responde 200 y bundle completo
    """
    current_user = _fake_auth_user()
    fake_uc = FakeGetBundleUseCase(mode="ok")
    app.dependency_overrides[get_current_user] = lambda: current_user
    app.dependency_overrides[get_public_bundle_use_case] = lambda: fake_uc
    client = TestClient(app)

    try:
        target_id = uuid4()
        res = client.get(
            f"/keys/{target_id}/bundle",
            headers={"Authorization": "Bearer sample_token"},
        )
        assert res.status_code == 200
        body = res.json()
        assert body["user_id"] == str(target_id)
        assert "identity_sign_pub" in body
        assert "signed_prekey_pub" in body
        assert "signature" in body
    finally:
        app.dependency_overrides.clear()


def test_get_bundle_endpoint_unauthorized():
    """
    ↳ GET /keys/{user_id}/bundle sin token responde 401 Unauthorized
    """
    client = TestClient(app)
    res = client.get(f"/keys/{uuid4()}/bundle")
    assert res.status_code == 401


def test_get_bundle_endpoint_user_not_found():
    """
    ↳ GET /keys/{user_id}/bundle cuando el usuario no existe responde 404
    """
    current_user = _fake_auth_user()
    fake_uc = FakeGetBundleUseCase(mode="not_found")
    app.dependency_overrides[get_current_user] = lambda: current_user
    app.dependency_overrides[get_public_bundle_use_case] = lambda: fake_uc
    client = TestClient(app)

    try:
        res = client.get(
            f"/keys/{uuid4()}/bundle",
            headers={"Authorization": "Bearer sample_token"},
        )
        assert res.status_code == 404
        assert res.json() == {"detail": "Target user not found"}
    finally:
        app.dependency_overrides.clear()


def test_get_bundle_endpoint_no_active_prekey():
    """
    ↳ GET /keys/{user_id}/bundle cuando el usuario no tiene prekey responde 404
    """
    current_user = _fake_auth_user()
    fake_uc = FakeGetBundleUseCase(mode="no_active")
    app.dependency_overrides[get_current_user] = lambda: current_user
    app.dependency_overrides[get_public_bundle_use_case] = lambda: fake_uc
    client = TestClient(app)

    try:
        res = client.get(
            f"/keys/{uuid4()}/bundle",
            headers={"Authorization": "Bearer sample_token"},
        )
        assert res.status_code == 404
        assert res.json() == {"detail": "No active prekey"}
    finally:
        app.dependency_overrides.clear()


def test_get_bundle_endpoint_prekey_expired():
    """
    ↳ GET /keys/{user_id}/bundle cuando la prekey expiró responde 404
    """
    current_user = _fake_auth_user()
    fake_uc = FakeGetBundleUseCase(mode="expired")
    app.dependency_overrides[get_current_user] = lambda: current_user
    app.dependency_overrides[get_public_bundle_use_case] = lambda: fake_uc
    client = TestClient(app)

    try:
        res = client.get(
            f"/keys/{uuid4()}/bundle",
            headers={"Authorization": "Bearer sample_token"},
        )
        assert res.status_code == 404
        assert res.json() == {"detail": "Prekey expired"}
    finally:
        app.dependency_overrides.clear()
