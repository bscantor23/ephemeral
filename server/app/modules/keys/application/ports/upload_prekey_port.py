from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.keys.domain.value_objects.prekey_bundle_response_vo import (
    PrekeyBundleResponseVO,
)
from app.modules.keys.domain.value_objects.upload_prekey_request_vo import (
    UploadPrekeyRequestVO,
)


class UploadPrekeyPort(ABC):
    @abstractmethod
    def execute(
        self, user_id: UUID, request: UploadPrekeyRequestVO
    ) -> PrekeyBundleResponseVO:
        ...
