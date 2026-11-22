from uuid import uuid4

from app.modules.keys.application.use_cases.upload_prekey_use_case import (
    UploadPrekeyUseCase,
)
from app.modules.keys.domain.entities.prekey_bundle_entity import (
    PrekeyBundleEntity,
)
from app.modules.keys.domain.ports.prekey_bundle_repository_port import (
    PrekeyBundleRepositoryPort,
)
from app.modules.keys.domain.value_objects.upload_prekey_request_vo import (
    UploadPrekeyRequestVO,
)


class FakePrekeyRepo(PrekeyBundleRepositoryPort):
    def __init__(self) -> None:
        self.deactivated_users: list = []
        self.saved_bundle: PrekeyBundleEntity | None = None

    def save(self, bundle: PrekeyBundleEntity) -> PrekeyBundleEntity:
        self.saved_bundle = bundle
        return bundle

    def get_active_by_user_id(self, user_id):
        return None

    def deactivate_all_for_user(self, user_id) -> None:
        self.deactivated_users.append(user_id)


def test_upload_prekey_use_case_success():
    """
    ↳ UploadPrekeyUseCase: desactiva prekeys previas y guarda nueva prekey activa
    """
    repo = FakePrekeyRepo()
    use_case = UploadPrekeyUseCase(prekey_repo=repo)

    user_id = uuid4()
    req = UploadPrekeyRequestVO(
        signed_prekey_pub="sample_spk_pub",
        signature="sample_spk_sig",
    )

    result = use_case.execute(user_id=user_id, request=req)

    assert user_id in repo.deactivated_users
    assert repo.saved_bundle is not None
    assert repo.saved_bundle.user_id == user_id
    assert repo.saved_bundle.signed_prekey_pub == "sample_spk_pub"
    assert repo.saved_bundle.signature == "sample_spk_sig"
    assert repo.saved_bundle.is_active is True

    assert result.user_id == user_id
    assert result.signed_prekey_pub == "sample_spk_pub"
    assert result.is_active is True
