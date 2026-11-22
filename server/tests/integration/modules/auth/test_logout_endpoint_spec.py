from fastapi.testclient import TestClient

from app.main import app
from app.modules.auth.application.ports.logout_user_port import LogoutUserPort
from app.modules.auth.infrastructure.inbound.http.dependencies import (
    get_logout_user_use_case,
)


class FakeLogoutUseCase(LogoutUserPort):
    def __init__(self) -> None:
        self.called_with = None

    def execute(self, raw_token: str) -> None:
        self.called_with = raw_token


def test_logout_endpoint_authenticated():
    """
    ↳ POST /auth/logout con cabecera de autorizacion responde 204 No Content
    """
    fake_uc = FakeLogoutUseCase()
    app.dependency_overrides[get_logout_user_use_case] = lambda: fake_uc
    client = TestClient(app)

    try:
        res = client.post(
            "/auth/logout", headers={"Authorization": "Bearer sample_token_123"}
        )
        assert res.status_code == 204
        assert fake_uc.called_with == "sample_token_123"
    finally:
        app.dependency_overrides.clear()


def test_logout_endpoint_without_token():
    """
    ↳ POST /auth/logout sin token responde 204 No Content sin invocar caso de uso
    """
    fake_uc = FakeLogoutUseCase()
    app.dependency_overrides[get_logout_user_use_case] = lambda: fake_uc
    client = TestClient(app)

    try:
        res = client.post("/auth/logout")
        assert res.status_code == 204
        assert fake_uc.called_with is None
    finally:
        app.dependency_overrides.clear()
