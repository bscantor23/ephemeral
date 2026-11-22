from uuid import UUID

from app.modules.keys.application.ports.upload_prekey_port import UploadPrekeyPort
from app.modules.keys.domain.entities.prekey_bundle_entity import (
    PrekeyBundleEntity,
)
from app.modules.keys.domain.ports.prekey_bundle_repository_port import (
    PrekeyBundleRepositoryPort,
)
from app.modules.keys.domain.value_objects.prekey_bundle_response_vo import (
    PrekeyBundleResponseVO,
)
from app.modules.keys.domain.value_objects.upload_prekey_request_vo import (
    UploadPrekeyRequestVO,
)


class UploadPrekeyUseCase(UploadPrekeyPort):
    def __init__(self, prekey_repo: PrekeyBundleRepositoryPort) -> None:
        self._prekey_repo = prekey_repo

    def execute(
        self, user_id: UUID, request: UploadPrekeyRequestVO
    ) -> PrekeyBundleResponseVO:
        self._prekey_repo.deactivate_all_for_user(user_id)

        entity = PrekeyBundleEntity.create(
            user_id=user_id,
            signed_prekey_pub=request.signed_prekey_pub,
            signature=request.signature,
        )
        saved = self._prekey_repo.save(entity)
        return PrekeyBundleResponseVO.from_entity(saved)
