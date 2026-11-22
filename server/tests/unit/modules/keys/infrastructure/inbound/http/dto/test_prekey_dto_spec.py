from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.modules.keys.domain.entities.prekey_bundle_entity import (
    PrekeyBundleEntity,
)
from app.modules.keys.domain.value_objects.public_bundle_response_vo import (
    PublicBundleResponseVO,
)
from app.modules.keys.infrastructure.inbound.http.dto.public_bundle_dto import (
    PublicBundleResponseDto,
)
from app.modules.keys.infrastructure.inbound.http.dto.upload_prekey_dto import (
    PrekeyBundleResponseDto,
    UploadPrekeyRequestDto,
)


def test_upload_prekey_request_dto_valid():
    """
    ↳ UploadPrekeyRequestDto: serialización y conversión a VO exitosa
    """
    dto = UploadPrekeyRequestDto(
        signed_prekey_pub="sample_spk_pub",
        signature="sample_sig",
    )
    req = dto.to_request()
    assert req.signed_prekey_pub == "sample_spk_pub"
    assert req.signature == "sample_sig"


def test_upload_prekey_request_dto_validation_error():
    """
    ↳ UploadPrekeyRequestDto: falla si signed_prekey_pub o signature están vacíos
    """
    with pytest.raises(ValidationError):
        UploadPrekeyRequestDto(signed_prekey_pub="", signature="sig")

    with pytest.raises(ValidationError):
        UploadPrekeyRequestDto(signed_prekey_pub="pub", signature="")


def test_prekey_bundle_response_dto():
    """
    ↳ PrekeyBundleResponseDto: serializa respuesta de prekey creada
    """
    pk_id = uuid4()
    u_id = uuid4()
    now = datetime.now(timezone.utc)
    dto = PrekeyBundleResponseDto(
        id=pk_id,
        user_id=u_id,
        signed_prekey_pub="spk",
        signature="sig",
        is_active=True,
        created_at=now,
        expires_at=now,
    )
    assert dto.id == pk_id
    assert dto.is_active is True


def test_public_bundle_response_dto_from_vo():
    """
    ↳ PublicBundleResponseDto: serializa respuesta completa para X3DH
    """
    vo = PublicBundleResponseVO(
        user_id=uuid4(),
        identity_sign_pub="isp",
        identity_dh_pub="idp",
        identity_dh_sig="ids",
        signed_prekey_id=uuid4(),
        signed_prekey_pub="spp",
        signature="sig",
        expires_at=datetime.now(timezone.utc),
    )
    dto = PublicBundleResponseDto(
        user_id=vo.user_id,
        identity_sign_pub=vo.identity_sign_pub,
        identity_dh_pub=vo.identity_dh_pub,
        identity_dh_sig=vo.identity_dh_sig,
        signed_prekey_id=vo.signed_prekey_id,
        signed_prekey_pub=vo.signed_prekey_pub,
        signature=vo.signature,
        expires_at=vo.expires_at,
    )
    assert dto.user_id == vo.user_id
    assert dto.signed_prekey_pub == "spp"
