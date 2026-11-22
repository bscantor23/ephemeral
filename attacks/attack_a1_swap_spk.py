#!/usr/bin/env python3
"""
Demostración de Ataque A1 — Sustitución de Signed Prekey (MITM en Servidor/DB).
Evaluación: Sección 5.5 del enunciado / Hito E5.

Escenario:
  1. Bob publica legítimamente su Prekey firmada con su clave de identidad ECDSA P-256.
  2. Un atacante con acceso a la base de datos (o servidor malicioso) sustituye
     'signed_prekey_pub' por una clave pública generada por el atacante (para intentar
     hacer MITM en el acuerdo Diffie-Hellman X3DH).
  3. Alice (el cliente) solicita el bundle público de Bob vía API: GET /keys/{bob_id}/bundle.
  4. Alice verifica criptográficamente la firma recibida contra la clave de identidad de Bob.

Resultado Esperado:
  La firma ECDSA falla matemáticamente. El cliente detecta la manipulación,
  aborta el establecimiento de sesión y no envía ningún mensaje.
"""

import base64
import sys
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import (
    decode_dss_signature,
    encode_dss_signature,
)
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat


def b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def b64url_decode(data: str) -> bytes:
    pad = "=" * ((4 - len(data) % 4) % 4)
    return base64.urlsafe_b64decode(data + pad)


def main():
    print("=" * 70)
    print("DEMOSTRACIÓN DE ATAQUE A1: Sustitución de Signed Prekey (MITM)")
    print("=" * 70)

    # 1. Bob genera su identidad legítima y su prekey firmada
    print("\n[1] Bob genera sus claves en su dispositivo:")
    bob_sign_priv = ec.generate_private_key(ec.SECP256R1())
    bob_sign_pub_raw = bob_sign_priv.public_key().public_bytes(
        Encoding.X962, PublicFormat.UncompressedPoint
    )

    bob_spk_priv = ec.generate_private_key(ec.SECP256R1())
    bob_spk_pub_raw = bob_spk_priv.public_key().public_bytes(
        Encoding.X962, PublicFormat.UncompressedPoint
    )

    # Bob firma su prekey legítima
    sig_der = bob_sign_priv.sign(bob_spk_pub_raw, ec.ECDSA(hashes.SHA256()))
    r, s = decode_dss_signature(sig_der)
    legitimate_signature_raw = r.to_bytes(32, "big") + s.to_bytes(32, "big")

    print(f"  * Bob Identity Sign Pub : {b64url_encode(bob_sign_pub_raw)[:32]}...")
    print(f"  * Bob Prekey Legítima   : {b64url_encode(bob_spk_pub_raw)[:32]}...")
    print(f"  * Bob Firma Legítima    : {b64url_encode(legitimate_signature_raw)[:32]}...")

    # 2. El Atacante / Servidor Deshonesto sustituye la prekey en la base de datos
    print("\n[2] ATACANTE con acceso a la BD ejecuta sustitución de prekey (swap_spk):")
    attacker_priv = ec.generate_private_key(ec.SECP256R1())
    attacker_spk_pub_raw = attacker_priv.public_key().public_bytes(
        Encoding.X962, PublicFormat.UncompressedPoint
    )
    print(f"  * Clave falsa inyectada : {b64url_encode(attacker_spk_pub_raw)[:32]}...")

    # El servidor devuelve: la clave del atacante + la firma vieja de Bob (porque el atacante NO tiene la clave privada de Bob)
    tampered_bundle = {
        "identity_sign_pub": b64url_encode(bob_sign_pub_raw),
        "signed_prekey_pub": b64url_encode(attacker_spk_pub_raw),  # ¡ALTERADA!
        "signature": b64url_encode(legitimate_signature_raw),
    }

    # 3. Alice consulta el bundle desde el servidor y verifica
    print("\n[3] Alice descarga el bundle y ejecuta verificación criptográfica:")
    received_sign_pub = ec.EllipticCurvePublicKey.from_encoded_point(
        ec.SECP256R1(), b64url_decode(tampered_bundle["identity_sign_pub"])
    )
    received_spk_bytes = b64url_decode(tampered_bundle["signed_prekey_pub"])
    raw_sig = b64url_decode(tampered_bundle["signature"])
    sig_to_verify = encode_dss_signature(
        int.from_bytes(raw_sig[:32], "big"), int.from_bytes(raw_sig[32:], "big")
    )

    try:
        received_sign_pub.verify(sig_to_verify, received_spk_bytes, ec.ECDSA(hashes.SHA256()))
        print("\n❌ FALLO DE SEGURIDAD: La firma fue aceptada (no debería ocurrir).")
        sys.exit(1)
    except Exception as e:
        print("\n✅ ATAQUE DETENIDO CON ÉXITO:")
        print("  * La verificación de firma ECDSA falló:", type(e).__name__)
        print("  * El cliente detectó que 'signed_prekey_pub' no fue firmada por la clave de identidad de Bob.")
        print("  * Consecuencia: Alice aborta la sesión X3DH y notifica alerta de MITM.")
    print("=" * 70)


if __name__ == "__main__":
    main()
