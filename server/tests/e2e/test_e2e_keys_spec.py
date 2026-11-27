from uuid import uuid4
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature
from fastapi.testclient import TestClient

from tests.e2e.conftest import register_and_login_helper
from tests.helpers.crypto_fixtures import (
    _b64url_decode,
    generate_client_identity,
    generate_signed_prekey,
)


def _verify_spk_signature(
    identity_sign_pub_b64: str,
    signed_prekey_pub_b64: str,
    signature_b64: str,
) -> bool:
    sign_pub_bytes = _b64url_decode(identity_sign_pub_b64)
    prekey_pub_bytes = _b64url_decode(signed_prekey_pub_b64)
    sig_raw = _b64url_decode(signature_b64)

    r = int.from_bytes(sig_raw[:32], byteorder="big")
    s = int.from_bytes(sig_raw[32:], byteorder="big")
    der_sig = encode_dss_signature(r, s)

    pub_key = ec.EllipticCurvePublicKey.from_encoded_point(
        ec.SECP256R1(), sign_pub_bytes
    )
    try:
        pub_key.verify(der_sig, prekey_pub_bytes, ec.ECDSA(hashes.SHA256()))
        return True
    except Exception:
        return False


def test_e2e_upload_and_fetch_bundle_success(e2e_client: TestClient):
    """
    ↳ Usuario autenticado publica Signed Prekey y otro usuario descarga bundle verificando criptograficamente la firma ECDSA
    """
    bob_keys = generate_client_identity()
    bob_user, bob_token, _ = register_and_login_helper(
        e2e_client, username="bob_keys", keys=bob_keys
    )
    _, alice_token, _ = register_and_login_helper(e2e_client, username="alice_keys")

    spk = generate_signed_prekey(bob_keys)
    upload_res = e2e_client.post(
        "/keys/prekey",
        json={
            "signed_prekey_pub": spk.prekey_pub_b64,
            "signature": spk.signature_b64,
        },
        headers={"Authorization": f"Bearer {bob_token}"},
    )
    assert upload_res.status_code == 201
    upload_data = upload_res.json()
    assert upload_data["signed_prekey_pub"] == spk.prekey_pub_b64
    assert upload_data["is_active"] is True

    bundle_res = e2e_client.get(
        f"/keys/{bob_user['id']}/bundle",
        headers={"Authorization": f"Bearer {alice_token}"},
    )
    assert bundle_res.status_code == 200
    bundle = bundle_res.json()
    assert bundle["user_id"] == bob_user["id"]
    assert bundle["identity_sign_pub"] == bob_keys.identity_sign_pub
    assert bundle["identity_dh_pub"] == bob_keys.identity_dh_pub
    assert bundle["signed_prekey_pub"] == spk.prekey_pub_b64
    assert bundle["signature"] == spk.signature_b64

    is_valid = _verify_spk_signature(
        identity_sign_pub_b64=bundle["identity_sign_pub"],
        signed_prekey_pub_b64=bundle["signed_prekey_pub"],
        signature_b64=bundle["signature"],
    )
    assert is_valid is True


def test_e2e_reupload_prekey_rotates_active_bundle(e2e_client: TestClient):
    """
    ↳ Publicar nueva prekey desactiva la anterior y actualiza el bundle publico servido
    """
    bob_keys = generate_client_identity()
    bob_user, bob_token, _ = register_and_login_helper(
        e2e_client, username="bob_rotate", keys=bob_keys
    )
    _, alice_token, _ = register_and_login_helper(e2e_client, username="alice_rotate")

    spk1 = generate_signed_prekey(bob_keys)
    e2e_client.post(
        "/keys/prekey",
        json={
            "signed_prekey_pub": spk1.prekey_pub_b64,
            "signature": spk1.signature_b64,
        },
        headers={"Authorization": f"Bearer {bob_token}"},
    )

    spk2 = generate_signed_prekey(bob_keys)
    upload2_res = e2e_client.post(
        "/keys/prekey",
        json={
            "signed_prekey_pub": spk2.prekey_pub_b64,
            "signature": spk2.signature_b64,
        },
        headers={"Authorization": f"Bearer {bob_token}"},
    )
    assert upload2_res.status_code == 201

    bundle_res = e2e_client.get(
        f"/keys/{bob_user['id']}/bundle",
        headers={"Authorization": f"Bearer {alice_token}"},
    )
    assert bundle_res.status_code == 200
    bundle = bundle_res.json()
    assert bundle["signed_prekey_pub"] == spk2.prekey_pub_b64
    assert bundle["signed_prekey_pub"] != spk1.prekey_pub_b64


def test_e2e_fetch_bundle_unregistered_user_fails(e2e_client: TestClient):
    """
    ↳ Consulta de bundle para usuario inexistente responde 404 Not Found
    """
    _, token, _ = register_and_login_helper(e2e_client, username="searcher")
    random_user_id = str(uuid4())

    res = e2e_client.get(
        f"/keys/{random_user_id}/bundle",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 404


def test_e2e_fetch_bundle_without_token_fails(e2e_client: TestClient):
    """
    ↳ Consulta de bundle sin autenticacion responde 401 Unauthorized
    """
    random_user_id = str(uuid4())
    res = e2e_client.get(f"/keys/{random_user_id}/bundle")
    assert res.status_code == 401


def test_e2e_upload_prekey_without_token_fails(e2e_client: TestClient):
    """
    ↳ Publicacion de prekey sin token responde 401 Unauthorized
    """
    res = e2e_client.post(
        "/keys/prekey",
        json={
            "signed_prekey_pub": "dummy_spk",
            "signature": "dummy_sig",
        },
    )
    assert res.status_code == 401
