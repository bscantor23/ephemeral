"""
Generador de credenciales criptográficas válidas para pruebas.

Simula lo que el cliente Flutter/Web/Python hace:
  1. Genera un par de claves ECDSA P-256 (firma de identidad).
  2. Genera un par de claves ECDH P-256 (acuerdo de claves Diffie-Hellman).
  3. Firma la clave pública DH con la clave privada de firma.
  4. Genera signed prekeys autenticadas.
  5. Ejecuta handshakes X3DH completos (emisor y receptor).
  6. Cifra y descifra mensajes simétricos con AES-256-GCM.
  7. Calcula números de seguridad (Safety Numbers) con SHA-512.
"""

import base64
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import os
from typing import Optional, Tuple
from uuid import UUID, uuid4

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import (
    decode_dss_signature,
    encode_dss_signature,
)
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat


def _b64url_encode(data: bytes) -> str:
    """Codifica bytes a base64url sin padding (formato WebCrypto / JWK)."""
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def _b64url_decode(data: str) -> bytes:
    """Decodifica un string base64url agregando el padding necesario."""
    pad = "=" * ((4 - len(data) % 4) % 4)
    return base64.urlsafe_b64decode(data + pad)


def _export_public_key_raw(private_key: ec.EllipticCurvePrivateKey) -> bytes:
    """Exporta la clave pública en formato X9.62 uncompressed (65 bytes para P-256)."""
    return private_key.public_key().public_bytes(
        encoding=Encoding.X962,
        format=PublicFormat.UncompressedPoint,
    )


def _sign_raw_rs(
    private_key: ec.EllipticCurvePrivateKey, data: bytes
) -> bytes:
    """
    Firma los datos con ECDSA-SHA256 y devuelve r || s en 64 bytes raw
    (formato IEEE P1363 / WebCrypto, sin envoltura DER/ASN.1).
    """
    signature_der = private_key.sign(data, ec.ECDSA(hashes.SHA256()))
    r, s = decode_dss_signature(signature_der)
    return r.to_bytes(32, byteorder="big") + s.to_bytes(32, byteorder="big")


@dataclass(frozen=True)
class ClientIdentityKeys:
    """Conjunto completo de claves de identidad de un cliente simulado."""

    identity_sign_pub: str
    identity_dh_pub: str
    identity_dh_sig: str

    _sign_private_key: ec.EllipticCurvePrivateKey
    _dh_private_key: ec.EllipticCurvePrivateKey

    _sign_pub_raw: bytes
    _dh_pub_raw: bytes


@dataclass(frozen=True)
class SignedPrekeyData:
    """Datos de una Signed Prekey generada localmente por el cliente."""

    prekey_pub_b64: str
    signature_b64: str
    _prekey_priv_key: ec.EllipticCurvePrivateKey
    _prekey_pub_raw: bytes


def generate_client_identity() -> ClientIdentityKeys:
    """
    Genera un conjunto completo de claves de identidad simulando un cliente.
    """
    sign_priv = ec.generate_private_key(ec.SECP256R1())
    sign_pub_raw = _export_public_key_raw(sign_priv)

    dh_priv = ec.generate_private_key(ec.SECP256R1())
    dh_pub_raw = _export_public_key_raw(dh_priv)

    dh_sig_raw = _sign_raw_rs(sign_priv, dh_pub_raw)

    return ClientIdentityKeys(
        identity_sign_pub=_b64url_encode(sign_pub_raw),
        identity_dh_pub=_b64url_encode(dh_pub_raw),
        identity_dh_sig=_b64url_encode(dh_sig_raw),
        _sign_private_key=sign_priv,
        _dh_private_key=dh_priv,
        _sign_pub_raw=sign_pub_raw,
        _dh_pub_raw=dh_pub_raw,
    )


def verify_identity_signature(keys: ClientIdentityKeys) -> bool:
    """
    Verifica que identity_dh_sig es una firma válida de identity_dh_pub
    usando identity_sign_pub.
    """
    sig_bytes = _b64url_decode(keys.identity_dh_sig)
    r = int.from_bytes(sig_bytes[:32], byteorder="big")
    s = int.from_bytes(sig_bytes[32:], byteorder="big")
    signature_der = encode_dss_signature(r, s)

    pub_key = keys._sign_private_key.public_key()
    dh_pub_bytes = _b64url_decode(keys.identity_dh_pub)

    try:
        pub_key.verify(signature_der, dh_pub_bytes, ec.ECDSA(hashes.SHA256()))
        return True
    except Exception:
        return False


def generate_signed_prekey(identity_keys: ClientIdentityKeys) -> SignedPrekeyData:
    """
    Genera un par de claves de prekey y las firma con la clave de identidad de firma.
    """
    spk_priv = ec.generate_private_key(ec.SECP256R1())
    spk_pub_raw = _export_public_key_raw(spk_priv)
    sig_raw = _sign_raw_rs(identity_keys._sign_private_key, spk_pub_raw)

    return SignedPrekeyData(
        prekey_pub_b64=_b64url_encode(spk_pub_raw),
        signature_b64=_b64url_encode(sig_raw),
        _prekey_priv_key=spk_priv,
        _prekey_pub_raw=spk_pub_raw,
    )


def simulate_x3dh_initiator(
    alice_keys: ClientIdentityKeys,
    bob_identity_dh_pub_b64: str,
    bob_spk_pub_b64: str,
) -> Tuple[bytes, str]:
    """
    Simula el cálculo X3DH del lado del emisor (Alice -> Bob).

    Calcula:
        DH1 = DH(IK_A, SPK_B)
        DH2 = DH(EK_A, IK_B)
        DH3 = DH(EK_A, SPK_B)
        SK  = HKDF(DH1 || DH2 || DH3)

    Returns:
        (session_key_32_bytes, ephemeral_pub_b64)
    """
    bob_ik_dh_bytes = _b64url_decode(bob_identity_dh_pub_b64)
    bob_spk_bytes = _b64url_decode(bob_spk_pub_b64)

    bob_ik_pub = ec.EllipticCurvePublicKey.from_encoded_point(
        ec.SECP256R1(), bob_ik_dh_bytes
    )
    bob_spk_pub = ec.EllipticCurvePublicKey.from_encoded_point(
        ec.SECP256R1(), bob_spk_bytes
    )

    # Clave efímera de Alice
    alice_ek_priv = ec.generate_private_key(ec.SECP256R1())
    alice_ek_pub_raw = _export_public_key_raw(alice_ek_priv)

    # Acuerdos Diffie-Hellman
    dh1 = alice_keys._dh_private_key.exchange(ec.ECDH(), bob_spk_pub)
    dh2 = alice_ek_priv.exchange(ec.ECDH(), bob_ik_pub)
    dh3 = alice_ek_priv.exchange(ec.ECDH(), bob_spk_pub)

    # Derivación HKDF-SHA256
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b"\x00" * 32,
        info=b"Ephemeral-E2EE-X3DH",
    )
    session_key = hkdf.derive(dh1 + dh2 + dh3)
    return session_key, _b64url_encode(alice_ek_pub_raw)


def simulate_x3dh_receiver(
    bob_keys: ClientIdentityKeys,
    bob_spk: SignedPrekeyData,
    alice_identity_dh_pub_b64: str,
    alice_ephemeral_pub_b64: str,
) -> bytes:
    """
    Simula el cálculo X3DH del lado del receptor (Bob recibiendo de Alice).

    Calcula:
        DH1 = DH(SPK_B, IK_A)
        DH2 = DH(IK_B, EK_A)
        DH3 = DH(SPK_B, EK_A)
        SK  = HKDF(DH1 || DH2 || DH3)

    Returns:
        session_key_32_bytes (idéntica a la generada por Alice)
    """
    alice_ik_dh_bytes = _b64url_decode(alice_identity_dh_pub_b64)
    alice_ek_bytes = _b64url_decode(alice_ephemeral_pub_b64)

    alice_ik_pub = ec.EllipticCurvePublicKey.from_encoded_point(
        ec.SECP256R1(), alice_ik_dh_bytes
    )
    alice_ek_pub = ec.EllipticCurvePublicKey.from_encoded_point(
        ec.SECP256R1(), alice_ek_bytes
    )

    # Acuerdos simétricos de Bob
    dh1 = bob_spk._prekey_priv_key.exchange(ec.ECDH(), alice_ik_pub)
    dh2 = bob_keys._dh_private_key.exchange(ec.ECDH(), alice_ek_pub)
    dh3 = bob_spk._prekey_priv_key.exchange(ec.ECDH(), alice_ek_pub)

    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b"\x00" * 32,
        info=b"Ephemeral-E2EE-X3DH",
    )
    return hkdf.derive(dh1 + dh2 + dh3)


def encrypt_message_aead(
    session_key: bytes,
    plaintext: str,
    msg_num: int,
    sender_id: UUID,
    recipient_id: UUID,
    protocol_version: int = 1,
) -> str:
    """
    Cifra el mensaje con AES-256-GCM y empaqueta nonce (12 bytes) + ciphertext + tag (16 bytes).

    Returns:
        String en base64url listo para enviar en el campo `ciphertext` de la API.
    """
    aesgcm = AESGCM(session_key)
    nonce = os.urandom(12)
    aad = f"{sender_id}:{recipient_id}:{protocol_version}:{msg_num}".encode("utf-8")
    encrypted = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), aad)
    return _b64url_encode(nonce + encrypted)


def decrypt_message_aead(
    session_key: bytes,
    ciphertext_b64: str,
    msg_num: int,
    sender_id: UUID,
    recipient_id: UUID,
    protocol_version: int = 1,
) -> str:
    """
    Descifra un payload base64url empaquetado (nonce + ciphertext + tag) con AES-256-GCM.

    Returns:
        Texto en claro recuperado.
    """
    raw_payload = _b64url_decode(ciphertext_b64)
    nonce = raw_payload[:12]
    encrypted_data_and_tag = raw_payload[12:]
    aad = f"{sender_id}:{recipient_id}:{protocol_version}:{msg_num}".encode("utf-8")

    aesgcm = AESGCM(session_key)
    decrypted = aesgcm.decrypt(nonce, encrypted_data_and_tag, aad)
    return decrypted.decode("utf-8")


def calculate_safety_number(pub1_raw: bytes, pub2_raw: bytes) -> str:
    """
    Calcula el Safety Number de 60 dígitos mediante SHA-512 de las claves públicas
    ordenadas lexicográficamente (formato Signal).
    """
    sorted_keys = sorted([pub1_raw, pub2_raw])
    digest = hashlib.sha512(sorted_keys[0] + sorted_keys[1]).digest()
    numbers = []
    for i in range(0, 30, 2):
        chunk = int.from_bytes(digest[i : i + 2], "big") % 100000
        numbers.append(f"{chunk:05d}")
    return " ".join(numbers[:12])


def build_register_payload(
    username: str,
    password: str = "Password123!",
    display_name: str = "",
    keys: Optional[ClientIdentityKeys] = None,
) -> dict:
    """
    Construye un payload JSON completo y criptográficamente válido
    para POST /auth/register.
    """
    if keys is None:
        keys = generate_client_identity()

    return {
        "username": username,
        "display_name": display_name or username.capitalize(),
        "password": password,
        "identity_sign_pub": keys.identity_sign_pub,
        "identity_dh_pub": keys.identity_dh_pub,
        "identity_dh_sig": keys.identity_dh_sig,
    }
