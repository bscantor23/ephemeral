from fastapi import Depends

from app.modules.users.application.ports.get_user_by_id_port import GetUserByIdPort
from app.modules.users.application.ports.get_user_by_username_port import (
    GetUserByUsernamePort,
)
from app.modules.users.application.ports.list_users_port import ListUsersPort
from app.modules.users.application.use_cases.get_user_by_id_use_case import (
    GetUserByIdUseCase,
)
from app.modules.users.application.use_cases.get_user_by_username_use_case import (
    GetUserByUsernameUseCase,
)
from app.modules.users.application.use_cases.list_users_use_case import (
    ListUsersUseCase,
)
from app.modules.users.domain.ports.user_directory_repository_port import (
    UserDirectoryRepositoryPort,
)
from app.modules.users.infrastructure.outbound.persistence.repositories.postgres_user_directory_repository import (
    PostgresUserDirectoryRepository,
)


def get_user_directory_repository() -> UserDirectoryRepositoryPort:
    return PostgresUserDirectoryRepository()


def get_list_users_use_case(
    repo: UserDirectoryRepositoryPort = Depends(get_user_directory_repository),
) -> ListUsersPort:
    return ListUsersUseCase(repository=repo)


def get_user_by_username_use_case(
    repo: UserDirectoryRepositoryPort = Depends(get_user_directory_repository),
) -> GetUserByUsernamePort:
    return GetUserByUsernameUseCase(repository=repo)


def get_user_by_id_use_case(
    repo: UserDirectoryRepositoryPort = Depends(get_user_directory_repository),
) -> GetUserByIdPort:
    return GetUserByIdUseCase(repository=repo)
