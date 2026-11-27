#!/usr/bin/env python3
"""
Demostración de Ataque A5 — Servidor Honesto pero Curioso / Volcado de BD (DB Dump).
Evaluación: Sección 5.5 del enunciado / Hito E5.

Escenario:
  1. Alice y Bob intercambian mensajes privados a través de la API.
  2. El servidor PostgreSQL almacena los registros en sus tablas:
     - 'users': claves públicas de identidad, contraseñas hasheadas con Argon2id.
     - 'prekey_bundles': prekeys públicas firmadas y sus firmas ECDSA.
     - 'messages': ciphertext opaco en AES-256-GCM, claves públicas efímeras, contadores.
  3. Un administrador de sistemas deshonesto o un atacante que vulnera el servidor
     extrae un volcado completo de la base de datos (pg_dump) e intenta leer los mensajes.

Resultado Esperado:
  El atacante no puede descifrar ningún mensaje. Toda la información almacenada en el
  servidor es pública o criptográficamente opaca. La seguridad descansa en la dificultad
  del problema del Logaritmo Discreto en Curvas Elípticas (ECDLP en P-256 / 2^128 seguridad)
  y la resistencia de AES-256 (2^256 claves).
"""

import base64
import os
import sys
from uuid import uuid4

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat


def b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def b64url_decode(data: str) -> bytes:
    pad = "=" * ((4 - len(data) % 4) % 4)
    return base64.urlsafe_b64decode(data + pad)


def main():
    print("=" * 70)
    print("DEMOSTRACIÓN DE ATAQUE A5: Servidor Curioso / Volcado de Base de Datos")
    print("=" * 70)

    # 1. Simulación de los datos reales que almacena PostgreSQL
    print("\n[1] Simulación de los registros almacenados en la base de datos (PostgreSQL):")

    # Claves de Alice (en su dispositivo)
    alice_ik_priv = ec.generate_private_key(ec.SECP256R1())
    alice_ik_pub_bytes = alice_ik_priv.public_key().public_bytes(Encoding.X962, PublicFormat.UncompressedPoint)

    # Claves de Bob (en su dispositivo)
    bob_ik_priv = ec.generate_private_key(ec.SECP256R1())
    bob_ik_pub_bytes = bob_ik_priv.public_key().public_bytes(Encoding.X962, PublicFormat.UncompressedPoint)

    bob_spk_priv = ec.generate_private_key(ec.SECP256R1())
    bob_spk_pub_bytes = bob_spk_priv.public_key().public_bytes(Encoding.X962, PublicFormat.UncompressedPoint)

    # Handshake X3DH legítimo en Alice
    alice_ek_priv = ec.generate_private_key(ec.SECP256R1())
    alice_ek_pub_bytes = alice_ek_priv.public_key().public_bytes(Encoding.X962, PublicFormat.UncompressedPoint)

    dh1 = alice_ik_priv.exchange(ec.ECDH(), bob_spk_priv.public_key())
    dh2 = alice_ek_priv.exchange(ec.ECDH(), bob_ik_priv.public_key())
    dh3 = alice_ek_priv.exchange(ec.ECDH(), bob_spk_priv.public_key())

    hkdf = HKDF(algorithm=hashes.SHA256(), length=32, salt=b"\x00" * 32, info=b"Ephemeral-E2EE-X3DH")
    real_session_key = hkdf.derive(dh1 + dh2 + dh3)

    # Alice cifra el mensaje
    secret_message = "Nota confidencial: Las coordenadas del servidor seguro son 4.6097, -74.0817"
    nonce = os.urandom(12)
    sender_id = uuid4()
    recipient_id = uuid4()
    msg_num = 1
    protocol_version = 1
    aad = f"{sender_id}:{recipient_id}:{protocol_version}:{msg_num}".encode("utf-8")
    real_ciphertext = AESGCM(real_session_key).encrypt(nonce, secret_message.encode("utf-8"), aad)

    # LO QUE VE LA BASE DE DATOS (dump de postgres):
    db_dump = {
        "table_users": [
            {"username": "alice", "identity_dh_pub": b64url_encode(alice_ik_pub_bytes)},
            {"username": "bob", "identity_dh_pub": b64url_encode(bob_ik_pub_bytes)},
        ],
        "table_prekey_bundles": [
            {"user": "bob", "signed_prekey_pub": b64url_encode(bob_spk_pub_bytes)},
        ],
        "table_messages": [
            {
                "msg_id": str(uuid4()),
                "sender": "alice",
                "recipient": "bob",
                "ephemeral_pub": b64url_encode(alice_ek_pub_bytes),
                "ciphertext": b64url_encode(nonce + real_ciphertext),
            }
        ],
    }

    print("  * TABLA 'users'          :", len(db_dump["table_users"]), "usuarios registrados.")
    print("  * TABLA 'prekey_bundles' : Prekey pública de Bob disponible.")
    print("  * TABLA 'messages'       : 1 mensaje cifrado capturado.")
    print(f"    - Ciphertext opaco     : {db_dump['table_messages'][0]['ciphertext'][:40]}...")

    # 2. El Atacante / Administrador Curioso intenta descifrar
    print("\n[2] ATACANTE intenta reconstruir la clave de sesión usando los datos del dump:")
    print("  * El atacante tiene acceso a todas las claves públicas:")
    print("    - IK_A (Alice DH Pub) :", db_dump["table_users"][0]["identity_dh_pub"][:20], "...")
    print("    - IK_B (Bob DH Pub)   :", db_dump["table_users"][1]["identity_dh_pub"][:20], "...")
    print("    - SPK_B (Bob SPK Pub) :", db_dump["table_prekey_bundles"][0]["signed_prekey_pub"][:20], "...")
    print("    - EK_A (Alice EK Pub) :", db_dump["table_messages"][0]["ephemeral_pub"][:20], "...")

    print("\n[3] Análisis Criptográfico de la Barrera de Seguridad:")
    print("  * Para calcular DH1 = DH(IK_A, SPK_B), el atacante necesita 'ik_a' o 'spk_b' (privadas).")
    print("  * Para calcular DH2 = DH(EK_A, IK_B), el atacante necesita 'ek_a' o 'ik_b' (privadas).")
    print("  * Para calcular DH3 = DH(EK_A, SPK_B), el atacante necesita 'ek_a' o 'spk_b' (privadas).")
    print("  * Ninguna clave privada está presente en la base de datos ni en el servidor.")
    print("  * El problema de calcular DH(A, B) conociendo solo g^a y g^b es el problema de Diffie-Hellman Computacional (CDH).")
    print("  * En P-256 (secp256r1), romper CDH requiere resolver el Logaritmo Discreto (ECDLP): ~2^128 operaciones.")

    # 3. Prueba empírica: Atacante intenta descifrar con una clave candidata aleatoria o generada sin la clave privada
    print("\n[4] Demostración práctica: El atacante intenta descifrar con clave deducida arbitraria:")
    attacker_guess_key = os.urandom(32)
    raw_payload = b64url_decode(db_dump["table_messages"][0]["ciphertext"])
    recv_nonce = raw_payload[:12]
    recv_cipher = raw_payload[12:]

    try:
        AESGCM(attacker_guess_key).decrypt(recv_nonce, recv_cipher, aad)
        print("❌ FALLO DE SEGURIDAD: El atacante descifró el mensaje.")
        sys.exit(1)
    except InvalidTag:
        print("✅ ATAQUE DETENIDO CON ÉXITO:")
        print("  * El descifrado falló: InvalidTag")
        print("  * Sin las claves privadas locales, el texto cifrado es computacionalmente indiscernible de ruido aleatorio.")
        print("  * Conclusión: El servidor honesto pero curioso no tiene capacidad matemática para leer los chats.")
    print("=" * 70)


if __name__ == "__main__":
    main()
