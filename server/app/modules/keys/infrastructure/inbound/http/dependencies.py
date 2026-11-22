from app.modules.auth.infrastructure.outbound.persistence.repositories.postgres_user_repository import (
    PostgresUserRepository,
)
from app.modules.keys.application.ports.get_public_bundle_port import (
    GetPublicBundlePort,
)
from app.modules.keys.application.ports.upload_prekey_port import UploadPrekeyPort
from app.modules.keys.application.use_cases.get_public_bundle_use_case import (
    GetPublicBundleUseCase,
)
from app.modules.keys.application.use_cases.upload_prekey_use_case import (
    UploadPrekeyUseCase,
)
from app.modules.keys.infrastructure.outbound.persistence.repositories.postgres_prekey_bundle_repository import (
    PostgresPrekeyBundleRepository,
)


def get_upload_prekey_use_case() -> UploadPrekeyPort:
    prekey_repo = PostgresPrekeyBundleRepository()
    return UploadPrekeyUseCase(prekey_repo=prekey_repo)


def get_public_bundle_use_case() -> GetPublicBundlePort:
    user_repo = PostgresUserRepository()
    prekey_repo = PostgresPrekeyBundleRepository()
    return GetPublicBundleUseCase(
        user_repo=user_repo,
        prekey_repo=prekey_repo,
    )
