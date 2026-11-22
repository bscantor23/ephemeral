"""
Generador de credenciales criptográficas válidas para pruebas.

Simula lo que el cliente Flutter haría al registrar un usuario:
  1. Genera un par de claves ECDSA P-256 (firma de identidad).
  2. Genera un par de claves ECDH P-256 (acuerdo de claves Diffie-Hellman).
  3. Firma la clave pública DH con la clave privada de firma.

Las claves privadas NUNCA se persisten; solo se usan dentro del test
para verificar firmas y simular el handshake criptográfico.
"""

import base64
from dataclasses import dataclass

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat


def _b64url_encode(data: bytes) -> str:
    """Codifica bytes a base64url sin padding (formato WebCrypto / JWK)."""
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


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
    signature_der = private_key.sign(data, ec.ECDSA(SHA256()))
    r, s = decode_dss_signature(signature_der)
    return r.to_bytes(32, byteorder="big") + s.to_bytes(32, byteorder="big")


@dataclass(frozen=True)
class ClientIdentityKeys:
    """Conjunto completo de claves de identidad de un cliente simulado."""

    # Claves públicas codificadas en base64url (lo que se envía al servidor)
    identity_sign_pub: str
    identity_dh_pub: str
    identity_dh_sig: str

    # Claves privadas (solo para verificaciones internas del test)
    _sign_private_key: ec.EllipticCurvePrivateKey
    _dh_private_key: ec.EllipticCurvePrivateKey

    # Bytes raw de las claves públicas (para verificaciones criptográficas)
    _sign_pub_raw: bytes
    _dh_pub_raw: bytes


def generate_client_identity() -> ClientIdentityKeys:
    """
    Genera un conjunto completo de claves de identidad simulando un cliente.

    Returns:
        ClientIdentityKeys con claves públicas en base64url listas para
        enviar al endpoint /auth/register, y las claves privadas para
        verificaciones internas del test.
    """
    # 1. Par de claves de firma (ECDSA P-256)
    sign_priv = ec.generate_private_key(ec.SECP256R1())
    sign_pub_raw = _export_public_key_raw(sign_priv)

    # 2. Par de claves de acuerdo DH (ECDH P-256)
    dh_priv = ec.generate_private_key(ec.SECP256R1())
    dh_pub_raw = _export_public_key_raw(dh_priv)

    # 3. Firma de la clave DH con la clave de firma
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
    usando identity_sign_pub. Simula la verificación que haría un
    cliente receptor al obtener el bundle de claves del servidor.

    Returns:
        True si la firma es criptográficamente válida.
    """
    from cryptography.hazmat.primitives.asymmetric.utils import (
        encode_dss_signature,
    )

    sig_bytes = base64.urlsafe_b64decode(keys.identity_dh_sig + "==")
    r = int.from_bytes(sig_bytes[:32], byteorder="big")
    s = int.from_bytes(sig_bytes[32:], byteorder="big")
    signature_der = encode_dss_signature(r, s)

    pub_key = keys._sign_private_key.public_key()
    dh_pub_bytes = base64.urlsafe_b64decode(keys.identity_dh_pub + "==")

    try:
        pub_key.verify(signature_der, dh_pub_bytes, ec.ECDSA(SHA256()))
        return True
    except Exception:
        return False


def build_register_payload(
    username: str,
    password: str = "Password123!",
    display_name: str = "",
    keys: ClientIdentityKeys | None = None,
) -> dict:
    """
    Construye un payload JSON completo y criptográficamente válido
    para POST /auth/register.

    Args:
        username: Nombre de usuario (3-32 caracteres alfanuméricos).
        password: Contraseña (mínimo 8 caracteres).
        display_name: Nombre para mostrar (opcional).
        keys: Claves de identidad pre-generadas; si es None, genera nuevas.

    Returns:
        dict listo para enviar como JSON al endpoint de registro.
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
