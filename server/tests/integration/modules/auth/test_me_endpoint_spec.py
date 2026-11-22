from datetime import datetime, timezone
from uuid import uuid4
from fastapi.testclient import TestClient

from app.main import app
from app.modules.auth.application.ports.validate_token_port import (
    ValidateTokenPort,
)
from app.modules.auth.domain.value_objects.user_response_vo import UserResponseVO
from app.modules.auth.infrastructure.outbound.security.auth_security import (
    get_validate_token_use_case,
)
from tests.helpers.crypto_fixtures import generate_client_identity


class FakeValidateTokenUseCase(ValidateTokenPort):
    def __init__(self) -> None:
        self._keys = generate_client_identity()

    def execute(self, raw_token: str) -> UserResponseVO:
        return UserResponseVO(
            id=uuid4(),
            username="eva",
            display_name="Eva",
            identity_sign_pub=self._keys.identity_sign_pub,
            identity_dh_pub=self._keys.identity_dh_pub,
            identity_dh_sig=self._keys.identity_dh_sig,
            created_at=datetime.now(timezone.utc),
        )


def test_me_endpoint_authenticated():
    """
    ↳ GET /auth/me con token valido responde 200 y perfil del usuario
    """
    app.dependency_overrides[get_validate_token_use_case] = lambda: FakeValidateTokenUseCase()
    client = TestClient(app)

    try:
        res = client.get("/auth/me", headers={"Authorization": "Bearer valid_token"})
        assert res.status_code == 200
        assert res.json()["username"] == "eva"
    finally:
        app.dependency_overrides.clear()


def test_me_endpoint_unauthorized():
    """
    ↳ GET /auth/me sin token responde 401 Unauthorized
    """
    client = TestClient(app)
    res = client.get("/auth/me")
    assert res.status_code == 401
