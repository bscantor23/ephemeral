from app.modules.keys.application.ports.get_public_bundle_port import (
    GetPublicBundlePort,
)
from app.modules.keys.application.ports.upload_prekey_port import UploadPrekeyPort
from app.modules.keys.infrastructure.inbound.http.dependencies import (
    get_public_bundle_use_case,
    get_upload_prekey_use_case,
)


def test_keys_dependencies_factories():
    """
    ↳ keys dependencies: las funciones factory entregan instancias válidas de los puertos
    """
    upload_uc = get_upload_prekey_use_case()
    bundle_uc = get_public_bundle_use_case()

    assert isinstance(upload_uc, UploadPrekeyPort)
    assert isinstance(bundle_uc, GetPublicBundlePort)
