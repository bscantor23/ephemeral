from typing import Optional
from uuid import UUID

from app.modules.auth.domain.ports.user_repository_port import (
    UserRepositoryPort,
)
from app.modules.keys.application.ports.get_public_bundle_port import (
    GetPublicBundlePort,
)
from app.modules.keys.domain.errors.keys_errors import (
    NoActivePrekeyError,
    TargetUserNotFoundError,
)
from app.modules.keys.domain.ports.prekey_bundle_repository_port import (
    PrekeyBundleRepositoryPort,
)
from app.modules.keys.domain.rules.keys_rules import KeysRules
from app.modules.keys.domain.value_objects.public_bundle_response_vo import (
    PublicBundleResponseVO,
)


class GetPublicBundleUseCase(GetPublicBundlePort):
    def __init__(
        self,
        user_repo: UserRepositoryPort,
        prekey_repo: PrekeyBundleRepositoryPort,
    ) -> None:
        self._user_repo = user_repo
        self._prekey_repo = prekey_repo

    def execute(self, target_user_id: UUID) -> PublicBundleResponseVO:
        user = self._user_repo.get_by_id(target_user_id)
        if user is None:
            raise TargetUserNotFoundError(
                f"User with id '{target_user_id}' was not found"
            )

        active_bundle = self._prekey_repo.get_active_by_user_id(target_user_id)
        if active_bundle is None:
            raise NoActivePrekeyError(
                f"User with id '{target_user_id}' has no active prekey bundle"
            )

        KeysRules.validate_not_expired(active_bundle.expires_at)

        return PublicBundleResponseVO(
            user_id=user.id,
            identity_sign_pub=user.identity_sign_pub,
            identity_dh_pub=user.identity_dh_pub,
            identity_dh_sig=user.identity_dh_sig,
            signed_prekey_id=active_bundle.id,
            signed_prekey_pub=active_bundle.signed_prekey_pub,
            signature=active_bundle.signature,
            expires_at=active_bundle.expires_at,
        )
