from datetime import datetime, timezone
from uuid import uuid4
import pytest

from app.modules.users.application.use_cases.get_user_by_username_use_case import (
    GetUserByUsernameUseCase,
)
from app.modules.users.domain.entities.user_profile_entity import UserProfileEntity
from app.modules.users.domain.errors.users_errors import UserNotFoundError


class FakeUsernameDirectoryRepo:
    def __init__(self, entity=None) -> None:
        self.entity = entity
        self.called_username = None

    def get_by_username(self, username: str):
        self.called_username = username
        return self.entity

    def get_by_id(self, user_id):
        ...

    def list_users(self, query):
        ...


def test_get_user_by_username_success():
    """
    ↳ GetUserByUsernameUseCase normaliza username y retorna UserProfileVO
    """
    uid = uuid4()
    now = datetime.now(timezone.utc)
    entity = UserProfileEntity(
        id=uid,
        username="bob",
        display_name="Bob M.",
        identity_sign_pub="sig_bob",
        identity_dh_pub="dh_bob",
        has_active_prekey=True,
        created_at=now,
    )
    repo = FakeUsernameDirectoryRepo(entity=entity)
    use_case = GetUserByUsernameUseCase(repository=repo)

    result = use_case.execute("@Bob")

    assert repo.called_username == "bob"
    assert result.id == uid
    assert result.username == "bob"
    assert result.display_name == "Bob M."
    assert result.has_active_prekey is True


def test_get_user_by_username_not_found():
    """
    ↳ GetUserByUsernameUseCase lanza UserNotFoundError si no existe
    """
    repo = FakeUsernameDirectoryRepo(entity=None)
    use_case = GetUserByUsernameUseCase(repository=repo)

    with pytest.raises(UserNotFoundError, match="User with username '@carol' was not found"):
        use_case.execute("carol")
