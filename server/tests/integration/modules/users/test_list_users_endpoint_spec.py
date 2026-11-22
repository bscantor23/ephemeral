from datetime import datetime, timezone
from uuid import uuid4
from fastapi.testclient import TestClient

from app.main import app
from app.modules.auth.domain.value_objects.user_response_vo import UserResponseVO
from app.modules.auth.infrastructure.outbound.security.auth_security import (
    get_current_user,
)
from app.modules.users.application.ports.list_users_port import ListUsersPort
from app.modules.users.domain.value_objects.list_users_vo import (
    ListUsersQueryVO,
    ListUsersResponseVO,
)
from app.modules.users.domain.value_objects.user_profile_vo import UserProfileVO
from app.modules.users.infrastructure.inbound.http.dependencies import (
    get_list_users_use_case,
)
from tests.helpers.crypto_fixtures import generate_client_identity


class FakeListUsersUseCase(ListUsersPort):
    def __init__(self, response: ListUsersResponseVO) -> None:
        self.response = response
        self.called_query = None

    def execute(self, query: ListUsersQueryVO) -> ListUsersResponseVO:
        self.called_query = query
        return self.response


def _fake_auth_user(user_id=None):
    uid = user_id or uuid4()
    keys = generate_client_identity()
    return UserResponseVO(
        id=uid,
        username="current_user",
        display_name="Current User",
        identity_sign_pub=keys.identity_sign_pub,
        identity_dh_pub=keys.identity_dh_pub,
        identity_dh_sig=keys.identity_dh_sig,
        created_at=datetime.now(timezone.utc),
    )


def test_list_users_endpoint_authenticated_success():
    """
    ↳ GET /users con token valido lista usuarios y estado de prekey
    """
    current_user = _fake_auth_user()
    user_vo = UserProfileVO(
        id=uuid4(),
        username="alice",
        display_name="Alice L.",
        identity_sign_pub="sig_pub_1",
        identity_dh_pub="dh_pub_1",
        has_active_prekey=True,
        created_at=datetime.now(timezone.utc),
    )
    fake_uc = FakeListUsersUseCase(
        ListUsersResponseVO(users=[user_vo], total=1, limit=50, offset=0)
    )

    app.dependency_overrides[get_current_user] = lambda: current_user
    app.dependency_overrides[get_list_users_use_case] = lambda: fake_uc
    client = TestClient(app)

    try:
        res = client.get("/users?search=alice&limit=10&offset=0")
        assert res.status_code == 200
        body = res.json()
        assert body["total"] == 1
        assert body["limit"] == 50
        assert len(body["users"]) == 1
        assert body["users"][0]["username"] == "alice"
        assert body["users"][0]["has_active_prekey"] is True
        assert fake_uc.called_query.exclude_user_id == current_user.id
    finally:
        app.dependency_overrides.clear()


def test_list_users_endpoint_unauthenticated():
    """
    ↳ GET /users sin token responde 401 Unauthorized
    """
    client = TestClient(app)
    res = client.get("/users")
    assert res.status_code == 401
