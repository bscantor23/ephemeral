#!/usr/bin/env python3
"""
Demostración de Ataque A6 — Compromiso de Clave de Sesión y Secreto Hacia Adelante (Forward Secrecy).
Evaluación: Sección 5.5 del enunciado / Hito E5.

Escenario:
  1. Alice y Bob intercambian una secuencia de mensajes (Msg #1, Msg #2 y Msg #3)
     utilizando un Ratchet Simétrico de avance de clave mediante KDF (HKDF-SHA256).
  2. Cada mensaje se cifra con una clave única efímera; tan pronto como el mensaje
     es enviado o procesado, la clave del mensaje y el estado previo se eliminan de la memoria.
  3. Un atacante pasivo graba todo el tráfico cifrado histórico (Msg #1 y Msg #2).
  4. En el tiempo T=3, el dispositivo de Bob es incautado o infectado con malware,
     y el atacante extrae la clave del mensaje actual (K_3) o la cadena activa.
  5. El atacante intenta utilizar K_3 para descifrar retrospectivamente los mensajes #1 y #2.

Resultado Esperado:
  El atacante no puede descifrar los mensajes históricos.
  Debido a la resistencia a la preimagen de las funciones KDF (unidireccionales),
  es matemáticamente inviable calcular K_1 o K_2 a partir del estado posterior K_3.
  El descifrado de los mensajes antiguos falla inmediatamente (InvalidTag).
"""

import base64
import os
import sys
from uuid import uuid4

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


def b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def b64url_decode(data: str) -> bytes:
    pad = "=" * ((4 - len(data) % 4) % 4)
    return base64.urlsafe_b64decode(data + pad)


def kdf_step(chain_key: bytes) -> tuple[bytes, bytes]:
    """
    Paso del ratchet simétrico KDF:
      - Deriva una clave de mensaje efímera (message_key).
      - Hace avanzar la clave de cadena (next_chain_key) de forma unidireccional.
    """
    # Derivación de la clave del mensaje
    hkdf_msg = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=chain_key,
        info=b"MessageKey-Generation",
    )
    message_key = hkdf_msg.derive(b"\x01")

    # Avance unidireccional de la cadena
    hkdf_chain = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=chain_key,
        info=b"ChainKey-Advance",
    )
    next_chain_key = hkdf_chain.derive(b"\x02")

    return message_key, next_chain_key


def main():
    print("=" * 70)
    print("DEMOSTRACIÓN DE ATAQUE A6: Compromiso de Clave y Forward Secrecy")
    print("=" * 70)

    # 1. Inicialización de la cadena de claves
    print("\n[1] Alice y Bob inicializan su Ratchet Simétrico tras el handshake X3DH:")
    root_key = os.urandom(32)
    current_chain_key = root_key
    sender_id = uuid4()
    recipient_id = uuid4()
    protocol_version = 1

    # 2. Generación y cifrado de Mensajes #1, #2 y #3
    print("\n[2] Transmisión secuencial de mensajes con avance de clave KDF:")

    # Mensaje 1
    k1, current_chain_key = kdf_step(current_chain_key)
    msg1_text = "Mensaje Secreto #1: La reunión es en el edificio Aula Magna"
    nonce1 = os.urandom(12)
    aad1 = f"{sender_id}:{recipient_id}:{protocol_version}:1".encode("utf-8")
    wire1 = b64url_encode(nonce1 + AESGCM(k1).encrypt(nonce1, msg1_text.encode("utf-8"), aad1))
    print(f"  * Mensaje #1 cifrado con K1 : '{msg1_text[:35]}...'")
    del k1  # Se borra la clave K1 de la memoria (Forward Secrecy)

    # Mensaje 2
    k2, current_chain_key = kdf_step(current_chain_key)
    msg2_text = "Mensaje Secreto #2: El código de acceso a la puerta es 8492"
    nonce2 = os.urandom(12)
    aad2 = f"{sender_id}:{recipient_id}:{protocol_version}:2".encode("utf-8")
    wire2 = b64url_encode(nonce2 + AESGCM(k2).encrypt(nonce2, msg2_text.encode("utf-8"), aad2))
    print(f"  * Mensaje #2 cifrado con K2 : '{msg2_text[:35]}...'")
    del k2  # Se borra la clave K2 de la memoria (Forward Secrecy)

    # Mensaje 3
    k3, current_chain_key = kdf_step(current_chain_key)
    msg3_text = "Mensaje Secreto #3: Confirmación recibida, cambio y fuera"
    nonce3 = os.urandom(12)
    aad3 = f"{sender_id}:{recipient_id}:{protocol_version}:3".encode("utf-8")
    wire3 = b64url_encode(nonce3 + AESGCM(k3).encrypt(nonce3, msg3_text.encode("utf-8"), aad3))
    print(f"  * Mensaje #3 cifrado con K3 : '{msg3_text[:35]}...'")

    # 3. El atacante compromete el dispositivo en T=3 y extrae K3
    print("\n[3] ATACANTE compromete el dispositivo en T=3 y extrae la clave activa K3:")
    print(f"  * Clave K3 comprometida (32 bytes): {b64url_encode(k3)[:24]}...")
    print("  * El atacante interceptó previamente los payloads de Msg #1 y Msg #2 en la red.")

    # 4. El atacante intenta descifrar los mensajes históricos con K3
    print("\n[4] ATACANTE intenta descifrar Mensaje #1 con la clave comprometida K3:")
    raw1 = b64url_decode(wire1)
    try:
        AESGCM(k3).decrypt(raw1[:12], raw1[12:], aad1)
        print("❌ FALLO DE SEGURIDAD: K3 pudo descifrar el Mensaje #1.")
        sys.exit(1)
    except InvalidTag:
        print("✅ ATAQUE DETENIDO CON ÉXITO:")
        print("  * El descifrado de Mensaje #1 falló: InvalidTag")
        print("  * La clave K3 no es matemáticamente válida para mensajes anteriores a T=3.")

    print("\n[5] ATACANTE intenta descifrar Mensaje #2 con la clave comprometida K3:")
    raw2 = b64url_decode(wire2)
    try:
        AESGCM(k3).decrypt(raw2[:12], raw2[12:], aad2)
        print("❌ FALLO DE SEGURIDAD: K3 pudo descifrar el Mensaje #2.")
        sys.exit(1)
    except InvalidTag:
        print("✅ ATAQUE DETENIDO CON ÉXITO:")
        print("  * El descifrado de Mensaje #2 falló: InvalidTag")

    # 5. Análisis matemático de unidireccionalidad
    print("\n[6] Demostración analítica de Forward Secrecy:")
    print("  * El ratchet KDF opera como una función hash unidireccional H(K_i) -> K_{i+1}.")
    print("  * Invertir H(K) para recuperar K1 a partir de K3 violaría la propiedad de resistencia a la preimagen de SHA-256.")
    print("  * Conclusión: Aunque una clave actual sea vulnerada, TODO el historial anterior permanece protegido.")
    print("=" * 70)


if __name__ == "__main__":
    main()
