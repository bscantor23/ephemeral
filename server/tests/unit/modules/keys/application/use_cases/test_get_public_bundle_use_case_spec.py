from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import uuid4

from app.modules.auth.domain.entities.user_entity import UserEntity
from app.modules.auth.domain.ports.user_repository_port import (
    UserRepositoryPort,
)
from app.modules.keys.application.use_cases.get_public_bundle_use_case import (
    GetPublicBundleUseCase,
)
from app.modules.keys.domain.entities.prekey_bundle_entity import (
    PrekeyBundleEntity,
)
from app.modules.keys.domain.errors.keys_errors import (
    NoActivePrekeyError,
    PrekeyExpiredError,
    TargetUserNotFoundError,
)
from app.modules.keys.domain.ports.prekey_bundle_repository_port import (
    PrekeyBundleRepositoryPort,
)


class FakeUserRepo(UserRepositoryPort):
    def __init__(self, user: Optional[UserEntity] = None) -> None:
        self.user = user

    def get_by_id(self, user_id):
        if self.user and self.user.id == user_id:
            return self.user
        return None

    def get_by_username(self, username):
        return None

    def save(self, user):
        return user


class FakePrekeyRepo(PrekeyBundleRepositoryPort):
    def __init__(self, bundle: Optional[PrekeyBundleEntity] = None) -> None:
        self.bundle = bundle

    def save(self, bundle):
        return bundle

    def get_active_by_user_id(self, user_id):
        if self.bundle and self.bundle.user_id == user_id:
            return self.bundle
        return None

    def deactivate_all_for_user(self, user_id) -> None:
        pass


def _create_sample_user(user_id=None):
    uid = user_id or uuid4()
    return UserEntity(
        id=uid,
        username="bob",
        display_name="Bob Dylan",
        password_hash="hash",
        identity_sign_pub="bob_sign_pub",
        identity_dh_pub="bob_dh_pub",
        identity_dh_sig="bob_dh_sig",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


def test_get_public_bundle_success():
    """
    ↳ GetPublicBundleUseCase: retorna bundle completo ensamblando usuario y prekey activa
    """
    user = _create_sample_user()
    bundle = PrekeyBundleEntity.create(
        user_id=user.id,
        signed_prekey_pub="bob_spk_pub",
        signature="bob_spk_sig",
        ttl_days=7,
    )

    user_repo = FakeUserRepo(user=user)
    prekey_repo = FakePrekeyRepo(bundle=bundle)
    use_case = GetPublicBundleUseCase(user_repo=user_repo, prekey_repo=prekey_repo)

    result = use_case.execute(target_user_id=user.id)

    assert result.user_id == user.id
    assert result.identity_sign_pub == "bob_sign_pub"
    assert result.identity_dh_pub == "bob_dh_pub"
    assert result.identity_dh_sig == "bob_dh_sig"
    assert result.signed_prekey_id == bundle.id
    assert result.signed_prekey_pub == "bob_spk_pub"
    assert result.signature == "bob_spk_sig"
    assert result.expires_at == bundle.expires_at


def test_get_public_bundle_user_not_found():
    """
    ↳ GetPublicBundleUseCase: lanza TargetUserNotFoundError si el target_user_id no existe
    """
    user_repo = FakeUserRepo(user=None)
    prekey_repo = FakePrekeyRepo(bundle=None)
    use_case = GetPublicBundleUseCase(user_repo=user_repo, prekey_repo=prekey_repo)

    try:
        use_case.execute(target_user_id=uuid4())
        assert False, "Debería haber lanzado TargetUserNotFoundError"
    except TargetUserNotFoundError as e:
        assert "not found" in str(e).lower()


def test_get_public_bundle_no_active_prekey():
    """
    ↳ GetPublicBundleUseCase: lanza NoActivePrekeyError si el usuario no tiene prekey activa
    """
    user = _create_sample_user()
    user_repo = FakeUserRepo(user=user)
    prekey_repo = FakePrekeyRepo(bundle=None)
    use_case = GetPublicBundleUseCase(user_repo=user_repo, prekey_repo=prekey_repo)

    try:
        use_case.execute(target_user_id=user.id)
        assert False, "Debería haber lanzado NoActivePrekeyError"
    except NoActivePrekeyError as e:
        assert "no active" in str(e).lower()


def test_get_public_bundle_expired_prekey():
    """
    ↳ GetPublicBundleUseCase: lanza PrekeyExpiredError si la prekey activa ha vencido
    """
    user = _create_sample_user()
    past = datetime.now(timezone.utc) - timedelta(days=1)
    bundle = PrekeyBundleEntity(
        id=uuid4(),
        user_id=user.id,
        signed_prekey_pub="expired_spk",
        signature="expired_sig",
        is_active=True,
        created_at=past - timedelta(days=7),
        expires_at=past,
    )

    user_repo = FakeUserRepo(user=user)
    prekey_repo = FakePrekeyRepo(bundle=bundle)
    use_case = GetPublicBundleUseCase(user_repo=user_repo, prekey_repo=prekey_repo)

    try:
        use_case.execute(target_user_id=user.id)
        assert False, "Debería haber lanzado PrekeyExpiredError"
    except PrekeyExpiredError as e:
        assert "expired" in str(e).lower()
