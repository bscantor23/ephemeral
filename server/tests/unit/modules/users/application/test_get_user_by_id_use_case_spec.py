from datetime import datetime, timezone
from uuid import uuid4
import pytest

from app.modules.users.application.use_cases.get_user_by_id_use_case import (
    GetUserByIdUseCase,
)
from app.modules.users.domain.entities.user_profile_entity import UserProfileEntity
from app.modules.users.domain.errors.users_errors import UserNotFoundError


class FakeIdDirectoryRepo:
    def __init__(self, entity=None) -> None:
        self.entity = entity
        self.called_id = None

    def get_by_id(self, user_id):
        self.called_id = user_id
        return self.entity

    def get_by_username(self, username):
        ...

    def list_users(self, query):
        ...


def test_get_user_by_id_success():
    """
    ↳ GetUserByIdUseCase consulta por UUID y retorna UserProfileVO
    """
    uid = uuid4()
    now = datetime.now(timezone.utc)
    entity = UserProfileEntity(
        id=uid,
        username="alice",
        display_name="Alice",
        identity_sign_pub="sig_alice",
        identity_dh_pub="dh_alice",
        has_active_prekey=False,
        created_at=now,
    )
    repo = FakeIdDirectoryRepo(entity=entity)
    use_case = GetUserByIdUseCase(repository=repo)

    result = use_case.execute(uid)

    assert repo.called_id == uid
    assert result.id == uid
    assert result.username == "alice"
    assert result.has_active_prekey is False


def test_get_user_by_id_not_found():
    """
    ↳ GetUserByIdUseCase lanza UserNotFoundError si UUID no existe
    """
    uid = uuid4()
    repo = FakeIdDirectoryRepo(entity=None)
    use_case = GetUserByIdUseCase(repository=repo)

    with pytest.raises(UserNotFoundError, match=f"User with id '{uid}' was not found"):
        use_case.execute(uid)
