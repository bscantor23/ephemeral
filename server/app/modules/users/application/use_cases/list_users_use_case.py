from app.modules.users.application.ports.list_users_port import ListUsersPort
from app.modules.users.domain.ports.user_directory_repository_port import (
    UserDirectoryRepositoryPort,
)
from app.modules.users.domain.rules.users_rules import UsersRules
from app.modules.users.domain.value_objects.list_users_vo import (
    ListUsersQueryVO,
    ListUsersResponseVO,
)
from app.modules.users.domain.value_objects.user_profile_vo import UserProfileVO


class ListUsersUseCase(ListUsersPort):
    def __init__(self, repository: UserDirectoryRepositoryPort) -> None:
        self._repository = repository

    def execute(self, query: ListUsersQueryVO) -> ListUsersResponseVO:
        UsersRules.validate_pagination(query.limit, query.offset)
        sanitized_search = UsersRules.validate_search_query(query.search)

        validated_query = ListUsersQueryVO(
            search=sanitized_search,
            limit=query.limit,
            offset=query.offset,
            exclude_user_id=query.exclude_user_id,
        )

        entities, total = self._repository.list_users(validated_query)

        vos = [
            UserProfileVO(
                id=u.id,
                username=u.username,
                display_name=u.display_name,
                identity_sign_pub=u.identity_sign_pub,
                identity_dh_pub=u.identity_dh_pub,
                has_active_prekey=u.has_active_prekey,
                created_at=u.created_at,
            )
            for u in entities
        ]

        return ListUsersResponseVO(
            users=vos,
            total=total,
            limit=query.limit,
            offset=query.offset,
        )
