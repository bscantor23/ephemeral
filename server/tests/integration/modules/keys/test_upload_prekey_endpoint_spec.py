from datetime import datetime, timezone
from uuid import uuid4
from fastapi.testclient import TestClient

from app.main import app
from app.modules.auth.domain.value_objects.user_response_vo import UserResponseVO
from app.modules.auth.infrastructure.outbound.security.auth_security import (
    get_current_user,
)
from app.modules.keys.application.ports.upload_prekey_port import UploadPrekeyPort
from app.modules.keys.domain.value_objects.prekey_bundle_response_vo import (
    PrekeyBundleResponseVO,
)
from app.modules.keys.domain.value_objects.upload_prekey_request_vo import (
    UploadPrekeyRequestVO,
)
from app.modules.keys.infrastructure.inbound.http.dependencies import (
    get_upload_prekey_use_case,
)
from tests.helpers.crypto_fixtures import generate_client_identity


class FakeUploadPrekeyUseCase(UploadPrekeyPort):
    def __init__(self) -> None:
        self.called_user_id = None
        self.called_request = None

    def execute(
        self, user_id: uuid4, request: UploadPrekeyRequestVO
    ) -> PrekeyBundleResponseVO:
        self.called_user_id = user_id
        self.called_request = request
        return PrekeyBundleResponseVO(
            id=uuid4(),
            user_id=user_id,
            signed_prekey_pub=request.signed_prekey_pub,
            signature=request.signature,
            is_active=True,
            created_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc),
        )


def _fake_auth_user(user_id=None):
    uid = user_id or uuid4()
    keys = generate_client_identity()
    return UserResponseVO(
        id=uid,
        username="alice",
        display_name="Alice Liddell",
        identity_sign_pub=keys.identity_sign_pub,
        identity_dh_pub=keys.identity_dh_pub,
        identity_dh_sig=keys.identity_dh_sig,
        created_at=datetime.now(timezone.utc),
    )


def test_upload_prekey_endpoint_authenticated_success():
    """
    ↳ POST /keys/prekey con token valido publica prekey y responde 201 Created
    """
    current_user = _fake_auth_user()
    fake_uc = FakeUploadPrekeyUseCase()
    app.dependency_overrides[get_current_user] = lambda: current_user
    app.dependency_overrides[get_upload_prekey_use_case] = lambda: fake_uc
    client = TestClient(app)

    try:
        keys = generate_client_identity()
        payload = {
            "signed_prekey_pub": keys.identity_dh_pub,
            "signature": keys.identity_dh_sig,
        }
        res = client.post(
            "/keys/prekey",
            headers={"Authorization": "Bearer sample_token"},
            json=payload,
        )
        assert res.status_code == 201
        body = res.json()
        assert body["user_id"] == str(current_user.id)
        assert body["signed_prekey_pub"] == keys.identity_dh_pub
        assert body["is_active"] is True
        assert fake_uc.called_user_id == current_user.id
    finally:
        app.dependency_overrides.clear()


def test_upload_prekey_endpoint_unauthorized():
    """
    ↳ POST /keys/prekey sin token responde 401 Unauthorized
    """
    client = TestClient(app)
    res = client.post("/keys/prekey", json={"signed_prekey_pub": "p", "signature": "s"})
    assert res.status_code == 401


def test_upload_prekey_endpoint_validation_error():
    """
    ↳ POST /keys/prekey con payload vacio responde 422
    """
    current_user = _fake_auth_user()
    app.dependency_overrides[get_current_user] = lambda: current_user
    client = TestClient(app)

    try:
        res = client.post(
            "/keys/prekey",
            headers={"Authorization": "Bearer sample_token"},
            json={"signed_prekey_pub": ""},
        )
        assert res.status_code == 422
    finally:
        app.dependency_overrides.clear()
