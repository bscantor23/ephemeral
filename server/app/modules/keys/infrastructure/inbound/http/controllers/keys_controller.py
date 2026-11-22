from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.modules.auth.domain.value_objects.user_response_vo import UserResponseVO
from app.modules.auth.infrastructure.outbound.security.auth_security import (
    get_current_user,
)
from app.modules.keys.application.ports.get_public_bundle_port import (
    GetPublicBundlePort,
)
from app.modules.keys.application.ports.upload_prekey_port import UploadPrekeyPort
from app.modules.keys.domain.value_objects.prekey_bundle_response_vo import (
    PrekeyBundleResponseVO,
)
from app.modules.keys.domain.value_objects.public_bundle_response_vo import (
    PublicBundleResponseVO,
)
from app.modules.keys.infrastructure.inbound.http.dependencies import (
    get_public_bundle_use_case,
    get_upload_prekey_use_case,
)
from app.modules.keys.infrastructure.inbound.http.dto.public_bundle_dto import (
    PublicBundleResponseDto,
)
from app.modules.keys.infrastructure.inbound.http.dto.upload_prekey_dto import (
    PrekeyBundleResponseDto,
    UploadPrekeyRequestDto,
)

router = APIRouter(prefix="/keys", tags=["Keys"])


@router.post(
    "/prekey",
    response_model=PrekeyBundleResponseDto,
    status_code=status.HTTP_201_CREATED,
)
def upload_prekey(
    dto: UploadPrekeyRequestDto,
    current_user: UserResponseVO = Depends(get_current_user),
    use_case: UploadPrekeyPort = Depends(get_upload_prekey_use_case),
) -> PrekeyBundleResponseVO:
    return use_case.execute(user_id=current_user.id, request=dto.to_request())


@router.get(
    "/{user_id}/bundle",
    response_model=PublicBundleResponseDto,
    status_code=status.HTTP_200_OK,
)
def get_public_bundle(
    user_id: UUID,
    _current_user: UserResponseVO = Depends(get_current_user),
    use_case: GetPublicBundlePort = Depends(get_public_bundle_use_case),
) -> PublicBundleResponseVO:
    return use_case.execute(target_user_id=user_id)
