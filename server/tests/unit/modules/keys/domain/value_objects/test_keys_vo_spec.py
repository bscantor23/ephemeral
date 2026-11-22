from datetime import datetime, timezone
from uuid import uuid4

from app.modules.keys.domain.entities.prekey_bundle_entity import (
    PrekeyBundleEntity,
)
from app.modules.keys.domain.value_objects.prekey_bundle_response_vo import (
    PrekeyBundleResponseVO,
)
from app.modules.keys.domain.value_objects.public_bundle_response_vo import (
    PublicBundleResponseVO,
)
from app.modules.keys.domain.value_objects.upload_prekey_request_vo import (
    UploadPrekeyRequestVO,
)


def test_upload_prekey_request_vo():
    """
    ↳ UploadPrekeyRequestVO: instanciación inmutable de solicitud de subida
    """
    vo = UploadPrekeyRequestVO(
        signed_prekey_pub="sp_pub",
        signature="sp_sig",
    )
    assert vo.signed_prekey_pub == "sp_pub"
    assert vo.signature == "sp_sig"


def test_prekey_bundle_response_vo_from_entity():
    """
    ↳ PrekeyBundleResponseVO: creación y from_entity correcto
    """
    entity = PrekeyBundleEntity.create(
        user_id=uuid4(),
        signed_prekey_pub="spk_pub",
        signature="spk_sig",
        ttl_days=7,
    )
    vo = PrekeyBundleResponseVO.from_entity(entity)
    assert vo.id == entity.id
    assert vo.user_id == entity.user_id
    assert vo.signed_prekey_pub == entity.signed_prekey_pub
    assert vo.signature == entity.signature
    assert vo.is_active == entity.is_active
    assert vo.created_at == entity.created_at
    assert vo.expires_at == entity.expires_at


def test_public_bundle_response_vo_creation():
    """
    ↳ PublicBundleResponseVO: estructura completa para X3DH
    """
    u_id = uuid4()
    spk_id = uuid4()
    exp = datetime.now(timezone.utc)

    vo = PublicBundleResponseVO(
        user_id=u_id,
        identity_sign_pub="isp",
        identity_dh_pub="idp",
        identity_dh_sig="ids",
        signed_prekey_id=spk_id,
        signed_prekey_pub="spp",
        signature="sig",
        expires_at=exp,
    )
    assert vo.user_id == u_id
    assert vo.identity_sign_pub == "isp"
    assert vo.identity_dh_pub == "idp"
    assert vo.identity_dh_sig == "ids"
    assert vo.signed_prekey_id == spk_id
    assert vo.signed_prekey_pub == "spp"
    assert vo.signature == "sig"
    assert vo.expires_at == exp
