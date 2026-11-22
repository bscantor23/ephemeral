from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.keys.domain.value_objects.public_bundle_response_vo import (
    PublicBundleResponseVO,
)


class GetPublicBundlePort(ABC):
    @abstractmethod
    def execute(self, target_user_id: UUID) -> PublicBundleResponseVO:
        ...
