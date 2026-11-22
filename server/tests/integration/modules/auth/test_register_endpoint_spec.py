from datetime import datetime, timezone
from uuid import uuid4
from fastapi.testclient import TestClient

from app.main import app
from app.modules.auth.application.ports.register_user_port import RegisterUserPort
from app.modules.auth.domain.errors.auth_errors import UserAlreadyExistsError
from app.modules.auth.domain.value_objects.register_user_request_vo import (
    RegisterUserRequestVO,
)
from app.modules.auth.domain.value_objects.user_response_vo import UserResponseVO
from app.modules.auth.infrastructure.inbound.http.dependencies import (
    get_register_user_use_case,
)
from tests.helpers.crypto_fixtures import (
    build_register_payload,
    generate_client_identity,
    verify_identity_signature,
)


class FakeRegisterUseCase(RegisterUserPort):
    def __init__(self, should_conflict: bool = False) -> None:
        self.should_conflict = should_conflict

    async def execute(self, request: RegisterUserRequestVO) -> UserResponseVO:
        if self.should_conflict:
            raise UserAlreadyExistsError("Username taken")
        return UserResponseVO(
            id=uuid4(),
            username=request.username,
            display_name=request.display_name,
            identity_sign_pub=request.identity_sign_pub,
            identity_dh_pub=request.identity_dh_pub,
            identity_dh_sig=request.identity_dh_sig,
            created_at=datetime.now(timezone.utc),
        )


def test_register_endpoint_success():
    """
    ↳ POST /auth/register responde 201 y perfil de usuario
    """
    app.dependency_overrides[get_register_user_use_case] = lambda: FakeRegisterUseCase()
    client = TestClient(app)

    try:
        payload = build_register_payload(username="eva_valid")
        res = client.post("/auth/register", json=payload)
        assert res.status_code == 201
        assert res.json()["username"] == "eva_valid"
    finally:
        app.dependency_overrides.clear()


def test_register_endpoint_with_valid_crypto_keys():
    """
    ↳ POST /auth/register con claves P-256 criptográficamente válidas responde 201
    """
    keys = generate_client_identity()
    app.dependency_overrides[get_register_user_use_case] = lambda: FakeRegisterUseCase()
    client = TestClient(app)

    try:
        payload = build_register_payload(username="crypto_user", keys=keys)
        res = client.post("/auth/register", json=payload)
        assert res.status_code == 201
        body = res.json()
        assert body["identity_sign_pub"] == keys.identity_sign_pub
        assert body["identity_dh_pub"] == keys.identity_dh_pub
        assert body["identity_dh_sig"] == keys.identity_dh_sig
    finally:
        app.dependency_overrides.clear()


def test_register_identity_signature_is_verifiable():
    """
    ↳ La firma identity_dh_sig generada por el cliente es verificable con identity_sign_pub
    """
    keys = generate_client_identity()
    assert verify_identity_signature(keys) is True


def test_register_endpoint_conflict():
    """
    ↳ POST /auth/register con username existente responde 409
    """
    app.dependency_overrides[get_register_user_use_case] = lambda: FakeRegisterUseCase(
        should_conflict=True
    )
    client = TestClient(app)

    try:
        payload = build_register_payload(username="eva_valid")
        res = client.post("/auth/register", json=payload)
        assert res.status_code == 409
    finally:
        app.dependency_overrides.clear()


def test_register_endpoint_validation_error():
    """
    ↳ POST /auth/register con payload incompleto responde 422
    """
    client = TestClient(app)
    res = client.post("/auth/register", json={"username": "ab"})
    assert res.status_code == 422
