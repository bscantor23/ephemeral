from app.modules.users.application.ports.get_user_by_username_port import (
    GetUserByUsernamePort,
)
from app.modules.users.domain.errors.users_errors import UserNotFoundError
from app.modules.users.domain.ports.user_directory_repository_port import (
    UserDirectoryRepositoryPort,
)
from app.modules.users.domain.rules.users_rules import UsersRules
from app.modules.users.domain.value_objects.user_profile_vo import UserProfileVO


class GetUserByUsernameUseCase(GetUserByUsernamePort):
    def __init__(self, repository: UserDirectoryRepositoryPort) -> None:
        self._repository = repository

    def execute(self, username: str) -> UserProfileVO:
        normalized = UsersRules.normalize_username(username)
        entity = self._repository.get_by_username(normalized)
        if entity is None:
            raise UserNotFoundError(f"User with username '@{normalized}' was not found")

        return UserProfileVO(
            id=entity.id,
            username=entity.username,
            display_name=entity.display_name,
            identity_sign_pub=entity.identity_sign_pub,
            identity_dh_pub=entity.identity_dh_pub,
            has_active_prekey=entity.has_active_prekey,
            created_at=entity.created_at,
        )
