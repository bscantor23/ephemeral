from collections.abc import Generator
from typing import Optional, Tuple
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.commons.db.all_models import Base
import app.commons.db.session as session_module
from app.main import app
from app.modules.auth.infrastructure.inbound.http.dependencies import (
    rate_limiter_singleton,
)
from app.modules.messages.infrastructure.inbound.websocket.connection_manager import (
    global_connection_manager,
)
from tests.helpers.crypto_fixtures import (
    ClientIdentityKeys,
    build_register_payload,
    generate_client_identity,
)


@pytest.fixture(autouse=True)
def e2e_db() -> Generator[None, None, None]:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    original_session_local = session_module.SessionLocal
    test_session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session_module.SessionLocal = test_session_local

    rate_limiter_singleton._attempts.clear()
    global_connection_manager._active_connections.clear()

    try:
        yield
    finally:
        Base.metadata.drop_all(engine)
        session_module.SessionLocal = original_session_local
        app.dependency_overrides.clear()
        rate_limiter_singleton._attempts.clear()
        global_connection_manager._active_connections.clear()


@pytest.fixture
def e2e_client() -> TestClient:
    return TestClient(app)


def register_and_login_helper(
    client: TestClient,
    username: str,
    password: str = "Password123!",
    display_name: str = "",
    keys: Optional[ClientIdentityKeys] = None,
) -> Tuple[dict, str, ClientIdentityKeys]:
    if keys is None:
        keys = generate_client_identity()
    payload = build_register_payload(
        username=username,
        password=password,
        display_name=display_name or username.capitalize(),
        keys=keys,
    )
    reg_res = client.post("/auth/register", json=payload)
    assert reg_res.status_code == 201, f"Register failed: {reg_res.text}"
    user_data = reg_res.json()

    login_res = client.post(
        "/auth/login", json={"username": username, "password": password}
    )
    assert login_res.status_code == 200, f"Login failed: {login_res.text}"
    token = login_res.json()["access_token"]
    return user_data, token, keys
