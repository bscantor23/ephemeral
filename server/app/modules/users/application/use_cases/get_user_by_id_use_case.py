from uuid import UUID

from app.modules.users.application.ports.get_user_by_id_port import GetUserByIdPort
from app.modules.users.domain.errors.users_errors import UserNotFoundError
from app.modules.users.domain.ports.user_directory_repository_port import (
    UserDirectoryRepositoryPort,
)
from app.modules.users.domain.value_objects.user_profile_vo import UserProfileVO


class GetUserByIdUseCase(GetUserByIdPort):
    def __init__(self, repository: UserDirectoryRepositoryPort) -> None:
        self._repository = repository

    def execute(self, user_id: UUID) -> UserProfileVO:
        entity = self._repository.get_by_id(user_id)
        if entity is None:
            raise UserNotFoundError(f"User with id '{user_id}' was not found")

        return UserProfileVO(
            id=entity.id,
            username=entity.username,
            display_name=entity.display_name,
            identity_sign_pub=entity.identity_sign_pub,
            identity_dh_pub=entity.identity_dh_pub,
            has_active_prekey=entity.has_active_prekey,
            created_at=entity.created_at,
        )
