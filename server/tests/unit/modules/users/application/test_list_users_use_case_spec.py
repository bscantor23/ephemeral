from datetime import datetime, timezone
from uuid import uuid4

from app.modules.users.application.use_cases.list_users_use_case import (
    ListUsersUseCase,
)
from app.modules.users.domain.entities.user_profile_entity import UserProfileEntity
from app.modules.users.domain.value_objects.list_users_vo import ListUsersQueryVO


class FakeDirectoryRepository:
    def __init__(self, entities=None, total=None) -> None:
        self.entities = entities or []
        self.total = total if total is not None else len(self.entities)
        self.called_query = None

    def list_users(self, query: ListUsersQueryVO):
        self.called_query = query
        return self.entities, self.total

    def get_by_id(self, user_id):
        ...

    def get_by_username(self, username):
        ...


def test_list_users_use_case_success():
    """
    ↳ ListUsersUseCase valida query, llama repositorio y mapea VOs
    """
    uid1 = uuid4()
    uid2 = uuid4()
    now = datetime.now(timezone.utc)
    entities = [
        UserProfileEntity(
            id=uid1,
            username="alice",
            display_name="Alice",
            identity_sign_pub="sig1",
            identity_dh_pub="dh1",
            has_active_prekey=True,
            created_at=now,
        ),
        UserProfileEntity(
            id=uid2,
            username="bob",
            display_name="Bob",
            identity_sign_pub="sig2",
            identity_dh_pub="dh2",
            has_active_prekey=False,
            created_at=now,
        ),
    ]

    repo = FakeDirectoryRepository(entities=entities, total=2)
    use_case = ListUsersUseCase(repository=repo)

    query = ListUsersQueryVO(search="  o  ", limit=10, offset=0)
    result = use_case.execute(query)

    assert result.total == 2
    assert result.limit == 10
    assert result.offset == 0
    assert len(result.users) == 2
    assert result.users[0].username == "alice"
    assert result.users[0].has_active_prekey is True
    assert result.users[1].username == "bob"
    assert result.users[1].has_active_prekey is False
    assert repo.called_query.search == "o"
