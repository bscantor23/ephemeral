from datetime import datetime, timezone
from uuid import uuid4
from fastapi.testclient import TestClient

from app.main import app
from app.modules.auth.application.ports.login_user_port import LoginUserPort
from app.modules.auth.domain.errors.auth_errors import (
    InvalidCredentialsError,
    RateLimitExceededError,
)
from app.modules.auth.domain.value_objects.login_user_request_vo import (
    LoginUserRequestVO,
)
from app.modules.auth.domain.value_objects.login_user_response_vo import (
    LoginUserResponseVO,
)
from app.modules.auth.domain.value_objects.user_response_vo import UserResponseVO
from app.modules.auth.infrastructure.inbound.http.dependencies import (
    get_login_user_use_case,
)


class FakeLoginUseCase(LoginUserPort):
    def __init__(self, mode: str = "ok") -> None:
        self.mode = mode

    async def execute(self, request: LoginUserRequestVO) -> LoginUserResponseVO:
        if self.mode == "rate_limit":
            raise RateLimitExceededError("Rate limit exceeded")
        if self.mode == "invalid":
            raise InvalidCredentialsError("Invalid credentials")
        user = UserResponseVO(
            id=uuid4(),
            username=request.username,
            display_name="User",
            identity_sign_pub="sp",
            identity_dh_pub="dp",
            identity_dh_sig="ds",
            created_at=datetime.now(timezone.utc),
        )
        return LoginUserResponseVO(
            access_token="fake_raw_token",
            token_type="bearer",
            expires_at=datetime.now(timezone.utc),
            user=user,
        )


def test_login_endpoint_success():
    """
    ↳ POST /auth/login con credenciales validas responde 200 y access_token
    """
    app.dependency_overrides[get_login_user_use_case] = lambda: FakeLoginUseCase(mode="ok")
    client = TestClient(app)

    try:
        res = client.post("/auth/login", json={"username": "eva", "password": "pass"})
        assert res.status_code == 200
        assert res.json()["access_token"] == "fake_raw_token"
        assert res.json()["token_type"] == "bearer"
    finally:
        app.dependency_overrides.clear()


def test_login_endpoint_rate_limited():
    """
    ↳ POST /auth/login con limite superado responde 429
    """
    app.dependency_overrides[get_login_user_use_case] = lambda: FakeLoginUseCase(
        mode="rate_limit"
    )
    client = TestClient(app)

    try:
        res = client.post("/auth/login", json={"username": "eva", "password": "pass"})
        assert res.status_code == 429
    finally:
        app.dependency_overrides.clear()


def test_login_endpoint_unauthorized():
    """
    ↳ POST /auth/login con credenciales invalidas responde 401
    """
    app.dependency_overrides[get_login_user_use_case] = lambda: FakeLoginUseCase(
        mode="invalid"
    )
    client = TestClient(app)

    try:
        res = client.post("/auth/login", json={"username": "eva", "password": "pass"})
        assert res.status_code == 401
    finally:
        app.dependency_overrides.clear()


def test_login_endpoint_validation_error():
    """
    ↳ POST /auth/login con body invalido responde 422
    """
    client = TestClient(app)
    res = client.post("/auth/login", json={"missing_password": "yes"})
    assert res.status_code == 422
