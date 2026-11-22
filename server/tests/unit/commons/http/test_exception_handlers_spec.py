from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from app.commons.errors.base_errors import ApplicationError, DomainError
from app.commons.http.exception_handlers import register_exception_handlers
from app.modules.auth.domain.errors.auth_errors import (
    InvalidCredentialsError,
    RateLimitExceededError,
    SessionExpiredError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.modules.health.domain.errors.health_errors import ServiceUnavailableError
from app.modules.keys.domain.errors.keys_errors import (
    NoActivePrekeyError,
    PrekeyExpiredError,
    TargetUserNotFoundError,
)


@pytest.fixture
def client():
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/test/service-unavailable")
    def raise_service_unavailable():
        raise ServiceUnavailableError("DB down")

    @app.get("/test/user-conflict")
    def raise_user_conflict():
        raise UserAlreadyExistsError("User exists")

    @app.get("/test/rate-limited")
    def raise_rate_limited():
        raise RateLimitExceededError("Too many attempts")

    @app.get("/test/invalid-credentials")
    def raise_invalid_credentials():
        raise InvalidCredentialsError("Bad credentials")

    @app.get("/test/session-expired")
    def raise_session_expired():
        raise SessionExpiredError("Session timed out")

    @app.get("/test/target-user-not-found")
    def raise_target_user_not_found():
        raise TargetUserNotFoundError("Target user not found")

    @app.get("/test/no-active-prekey")
    def raise_no_active_prekey():
        raise NoActivePrekeyError("No active prekey")

    @app.get("/test/prekey-expired")
    def raise_prekey_expired():
        raise PrekeyExpiredError("Prekey expired")

    @app.get("/test/user-not-found")
    def raise_user_not_found():
        raise UserNotFoundError("User gone")

    @app.get("/test/generic-domain")
    def raise_generic_domain():
        raise DomainError("Invalid domain state")

    @app.get("/test/generic-app")
    def raise_generic_app():
        raise ApplicationError("Invalid app orchestration")

    return TestClient(app, raise_server_exceptions=False)


def test_exception_handler_service_unavailable(client):
    """
    ↳ Handlers: ServiceUnavailableError mapea a HTTP 503
    """
    res = client.get("/test/service-unavailable")
    assert res.status_code == 503
    assert res.json() == {"detail": "DB down"}


def test_exception_handler_user_conflict(client):
    """
    ↳ Handlers: UserAlreadyExistsError mapea a HTTP 409
    """
    res = client.get("/test/user-conflict")
    assert res.status_code == 409
    assert res.json() == {"detail": "User exists"}


def test_exception_handler_rate_limited(client):
    """
    ↳ Handlers: RateLimitExceededError mapea a HTTP 429
    """
    res = client.get("/test/rate-limited")
    assert res.status_code == 429
    assert res.json() == {"detail": "Too many attempts"}


def test_exception_handler_invalid_credentials(client):
    """
    ↳ Handlers: InvalidCredentialsError mapea a HTTP 401
    """
    res = client.get("/test/invalid-credentials")
    assert res.status_code == 401
    assert res.json() == {"detail": "Bad credentials"}


def test_exception_handler_session_expired(client):
    """
    ↳ Handlers: SessionExpiredError mapea a HTTP 401
    """
    res = client.get("/test/session-expired")
    assert res.status_code == 401
    assert res.json() == {"detail": "Session timed out"}


def test_exception_handler_target_user_not_found(client):
    """
    ↳ Handlers: TargetUserNotFoundError mapea a HTTP 404
    """
    res = client.get("/test/target-user-not-found")
    assert res.status_code == 404
    assert res.json() == {"detail": "Target user not found"}


def test_exception_handler_no_active_prekey(client):
    """
    ↳ Handlers: NoActivePrekeyError mapea a HTTP 404
    """
    res = client.get("/test/no-active-prekey")
    assert res.status_code == 404
    assert res.json() == {"detail": "No active prekey"}


def test_exception_handler_prekey_expired(client):
    """
    ↳ Handlers: PrekeyExpiredError mapea a HTTP 404
    """
    res = client.get("/test/prekey-expired")
    assert res.status_code == 404
    assert res.json() == {"detail": "Prekey expired"}


def test_exception_handler_user_not_found(client):
    """
    ↳ Handlers: UserNotFoundError mapea a HTTP 401
    """
    res = client.get("/test/user-not-found")
    assert res.status_code == 401
    assert res.json() == {"detail": "User gone"}


def test_exception_handler_generic_domain(client):
    """
    ↳ Handlers: DomainError generico mapea a HTTP 422
    """
    res = client.get("/test/generic-domain")
    assert res.status_code == 422
    assert res.json() == {"detail": "Invalid domain state"}


def test_exception_handler_generic_app(client):
    """
    ↳ Handlers: ApplicationError generico mapea a HTTP 400
    """
    res = client.get("/test/generic-app")
    assert res.status_code == 400
    assert res.json() == {"detail": "Invalid app orchestration"}
