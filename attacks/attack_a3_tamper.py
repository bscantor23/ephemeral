#!/usr/bin/env python3
"""
Demostración de Ataque A3 — Modificación de Mensaje Cifrado en Tránsito (Tampering).
Evaluación: Sección 5.5 del enunciado / Hito E5.

Escenario:
  1. Alice y Bob tienen una sesión E2EE establecida con una clave compartida derivada vía X3DH.
  2. Alice cifra un mensaje auténtico: "Transferir $1000 a Charlie".
  3. El mensaje se protege con cifrado autenticado AEAD (AES-256-GCM), autenticando
     los metadatos críticos en los Datos Asociados (AAD): sender_id, recipient_id, msg_num.
  4. Un atacante en red (o el servidor deshonesto) intercepta la carga útil y altera
     un solo byte del texto cifrado (por ejemplo, para cambiar la cantidad o los datos).
  5. Bob recibe el mensaje modificado e intenta procesarlo.

Resultado Esperado:
  La verificación matemática del Authentication Tag (GCM) falla inmediatamente.
  El cliente Bob rechaza la carga completa, descarta el mensaje y registra una alerta
  de violación de integridad, sin exponer jamás datos corruptos a la aplicación.
"""

import base64
import os
import sys
from uuid import uuid4

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def b64url_decode(data: str) -> bytes:
    pad = "=" * ((4 - len(data) % 4) % 4)
    return base64.urlsafe_b64decode(data + pad)


def main():
    print("=" * 70)
    print("DEMOSTRACIÓN DE ATAQUE A3: Modificación de Mensaje en Tránsito (Tamper)")
    print("=" * 70)

    # 1. Parámetros de sesión y clave compartida de 256 bits
    print("\n[1] Sesión activa entre Alice y Bob (Clave derivada vía X3DH):")
    session_key = os.urandom(32)
    sender_id = uuid4()
    recipient_id = uuid4()
    msg_num = 1
    protocol_version = 1

    original_text = "Transferir $1000 a Charlie - Autorizado por Alice"
    print(f"  * Mensaje original de Alice : {original_text}")
    print(f"  * Clave de sesión (32 bytes): {b64url_encode(session_key)[:24]}...")

    # 2. Alice cifra con AES-256-GCM autenticando metadatos en AAD
    print("\n[2] Alice cifra el mensaje con AES-256-GCM y datos asociados (AAD):")
    aesgcm = AESGCM(session_key)
    nonce = os.urandom(12)
    aad = f"{sender_id}:{recipient_id}:{protocol_version}:{msg_num}".encode("utf-8")

    encrypted_payload = aesgcm.encrypt(nonce, original_text.encode("utf-8"), aad)
    wire_payload = nonce + encrypted_payload
    wire_b64 = b64url_encode(wire_payload)

    print(f"  * Nonce (12 bytes)           : {b64url_encode(nonce)}")
    print(f"  * Payload cifrado + Tag GCM  : {wire_b64[:36]}... ({len(wire_payload)} bytes)")
    print(f"  * Datos asociados (AAD)      : {aad.decode('utf-8')}")

    # 3. El atacante intercepta y modifica 1 byte del texto cifrado (Tampering)
    print("\n[3] ATACANTE intercepta el mensaje y altera bytes del texto cifrado:")
    raw_bytes = bytearray(b64url_decode(wire_b64))

    # Modificar un byte en el medio del payload cifrado
    tampered_index = 12 + 5  # Dentro del ciphertext
    raw_bytes[tampered_index] ^= 0xFF  # Invierte todos los bits de ese byte
    tampered_b64 = b64url_encode(bytes(raw_bytes))

    print(f"  * Byte modificado en índice  : {tampered_index}")
    print(f"  * Payload manipulado (tamper): {tampered_b64[:36]}...")

    # 4. Bob recibe la carga alterada e intenta descifrar
    print("\n[4] Bob recibe el mensaje manipulado y ejecuta descifrado AEAD:")
    received_bytes = b64url_decode(tampered_b64)
    recv_nonce = received_bytes[:12]
    recv_ciphertext_and_tag = received_bytes[12:]

    try:
        decrypted_bytes = aesgcm.decrypt(recv_nonce, recv_ciphertext_and_tag, aad)
        print("\n❌ FALLO DE SEGURIDAD: El mensaje alterado fue aceptado.")
        sys.exit(1)
    except InvalidTag:
        print("\n✅ ATAQUE DETENIDO CON ÉXITO:")
        print("  * La verificación del Authentication Tag (GCM) falló: InvalidTag")
        print("  * El cliente Bob detectó que el ciphertext fue manipulado en tránsito.")
        print("  * Consecuencia: El payload es descartado en memoria sin llegar a la UI.")
    except Exception as e:
        print(f"\n✅ ATAQUE DETENIDO: Error inesperado de verificación: {e}")

    # 5. Escenario adicional: Alteración en los Datos Asociados (AAD)
    print("\n[5] ATACANTE intenta alterar los datos asociados (cambiar sender_id o msg_num):")
    tampered_aad = f"{uuid4()}:{recipient_id}:{protocol_version}:{msg_num}".encode("utf-8")
    try:
        aesgcm.decrypt(nonce, encrypted_payload, tampered_aad)
        print("❌ FALLO DE SEGURIDAD: Los datos asociados manipulados fueron aceptados.")
        sys.exit(1)
    except InvalidTag:
        print("✅ ATAQUE DETENIDO CON ÉXITO:")
        print("  * La verificación del Tag falló al cambiar el AAD: InvalidTag")
        print("  * Consecuencia: Nadie puede suplantar al remitente ni alterar el número de secuencia.")
    print("=" * 70)


if __name__ == "__main__":
    main()
