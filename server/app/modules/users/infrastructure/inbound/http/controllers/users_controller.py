from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status

from app.modules.auth.domain.value_objects.user_response_vo import UserResponseVO
from app.modules.auth.infrastructure.outbound.security.auth_security import (
    get_current_user,
)
from app.modules.users.application.ports.get_user_by_id_port import GetUserByIdPort
from app.modules.users.application.ports.get_user_by_username_port import (
    GetUserByUsernamePort,
)
from app.modules.users.application.ports.list_users_port import ListUsersPort
from app.modules.users.domain.constants.users_constants import DEFAULT_USERS_LIMIT
from app.modules.users.domain.value_objects.list_users_vo import ListUsersQueryVO
from app.modules.users.infrastructure.inbound.http.dependencies import (
    get_list_users_use_case,
    get_user_by_id_use_case,
    get_user_by_username_use_case,
)
from app.modules.users.infrastructure.inbound.http.dto.user_profile_dto import (
    ListUsersResponseDTO,
    UserProfileResponseDTO,
)
from app.modules.users.infrastructure.outbound.persistence.mappers.user_profile_mapper import (
    UserProfileMapper,
)

router = APIRouter(tags=["Users"])


@router.get(
    "",
    response_model=ListUsersResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Listar usuarios del directorio",
)
def list_users(
    search: Optional[str] = Query(default=None, description="Filtro de búsqueda por username o display_name"),
    limit: int = Query(default=DEFAULT_USERS_LIMIT, ge=1, le=100, description="Límite de resultados"),
    offset: int = Query(default=0, ge=0, description="Desplazamiento para paginación"),
    current_user: UserResponseVO = Depends(get_current_user),
    use_case: ListUsersPort = Depends(get_list_users_use_case),
) -> ListUsersResponseDTO:
    query = ListUsersQueryVO(
        search=search,
        limit=limit,
        offset=offset,
        exclude_user_id=current_user.id,
    )
    result = use_case.execute(query)
    return ListUsersResponseDTO(
        users=[UserProfileMapper.to_dto(u) for u in result.users],
        total=result.total,
        limit=result.limit,
        offset=result.offset,
    )


@router.get(
    "/by-username/{username}",
    response_model=UserProfileResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Buscar usuario por @username",
)
def get_user_by_username(
    username: str,
    _: UserResponseVO = Depends(get_current_user),
    use_case: GetUserByUsernamePort = Depends(get_user_by_username_use_case),
) -> UserProfileResponseDTO:
    result = use_case.execute(username)
    return UserProfileMapper.to_dto(result)


@router.get(
    "/{user_id}",
    response_model=UserProfileResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Obtener perfil público por UUID",
)
def get_user_by_id(
    user_id: UUID,
    _: UserResponseVO = Depends(get_current_user),
    use_case: GetUserByIdPort = Depends(get_user_by_id_use_case),
) -> UserProfileResponseDTO:
    result = use_case.execute(user_id)
    return UserProfileMapper.to_dto(result)
