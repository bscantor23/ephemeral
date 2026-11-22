from typing import Protocol

from app.modules.users.domain.value_objects.list_users_vo import (
    ListUsersQueryVO,
    ListUsersResponseVO,
)


class ListUsersPort(Protocol):
    def execute(self, query: ListUsersQueryVO) -> ListUsersResponseVO:
        ...
