from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from app.modules.keys.domain.entities.prekey_bundle_entity import (
    PrekeyBundleEntity,
)


class PrekeyBundleRepositoryPort(ABC):
    @abstractmethod
    def save(self, bundle: PrekeyBundleEntity) -> PrekeyBundleEntity:
        ...

    @abstractmethod
    def get_active_by_user_id(self, user_id: UUID) -> Optional[PrekeyBundleEntity]:
        ...

    @abstractmethod
    def deactivate_all_for_user(self, user_id: UUID) -> None:
        ...
