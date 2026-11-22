from app.modules.users.application.use_cases.get_user_by_id_use_case import (
    GetUserByIdUseCase,
)
from app.modules.users.application.use_cases.get_user_by_username_use_case import (
    GetUserByUsernameUseCase,
)
from app.modules.users.application.use_cases.list_users_use_case import (
    ListUsersUseCase,
)
from app.modules.users.infrastructure.inbound.http.dependencies import (
    get_list_users_use_case,
    get_user_by_id_use_case,
    get_user_by_username_use_case,
    get_user_directory_repository,
)
from app.modules.users.infrastructure.outbound.persistence.repositories.postgres_user_directory_repository import (
    PostgresUserDirectoryRepository,
)


def test_users_dependencies():
    """
    ↳ Proveedores de dependencias retornan instancias correctas
    """
    repo = get_user_directory_repository()
    assert isinstance(repo, PostgresUserDirectoryRepository)

    list_uc = get_list_users_use_case(repo=repo)
    assert isinstance(list_uc, ListUsersUseCase)

    get_username_uc = get_user_by_username_use_case(repo=repo)
    assert isinstance(get_username_uc, GetUserByUsernameUseCase)

    get_id_uc = get_user_by_id_use_case(repo=repo)
    assert isinstance(get_id_uc, GetUserByIdUseCase)
