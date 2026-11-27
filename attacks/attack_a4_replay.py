#!/usr/bin/env python3
"""
Demostración de Ataque A4 — Reenvío de Mensaje Cifrado Antiguo (Replay Attack).
Evaluación: Sección 5.5 del enunciado / Hito E5.

Escenario:
  1. Alice envía legítimamente el mensaje #1 ("Transferir $50 a David") a Bob.
  2. Bob recibe, verifica el contador (msg_num=1), descifra y actualiza su estado.
  3. Alice envía posteriormente el mensaje #2 ("Transferir $20 a David") con msg_num=2.
  4. Un atacante pasivo que interceptó el mensaje #1 en la red o en la API intenta
     reinyectarlo para que Bob procese una segunda transferencia duplicada.

Resultado Esperado:
  El mecanismo dual de defensa detiene el ataque:
    - Escenario A (Reenvío directo): Bob detecta que msg_num <= last_seen_msg_num y lo descarta.
    - Escenario B (Atacante altera msg_num en tránsito para eludir el contador): Falla
      la verificación del Authentication Tag (AEAD) porque msg_num está autenticado en los AAD.
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
    print("DEMOSTRACIÓN DE ATAQUE A4: Reenvío de Mensajes Cifrados (Replay Attack)")
    print("=" * 70)

    session_key = os.urandom(32)
    aesgcm = AESGCM(session_key)
    sender_id = uuid4()
    recipient_id = uuid4()
    protocol_version = 1

    # Estado local de Bob (contador de secuencia de mensajes recibidos)
    bob_last_seen_msg_num = 0

    def bob_receive(wire_b64: str, msg_num: int) -> str:
        nonlocal bob_last_seen_msg_num
        # 1. Validación de contador monotónico contra Replay
        if msg_num <= bob_last_seen_msg_num:
            raise ValueError(
                f"REPLAY DETECTADO: msg_num={msg_num} es menor o igual al último procesado ({bob_last_seen_msg_num})"
            )

        # 2. Descifrado autenticado con AAD conteniendo msg_num
        raw = b64url_decode(wire_b64)
        nonce = raw[:12]
        ciphertext_and_tag = raw[12:]
        aad = f"{sender_id}:{recipient_id}:{protocol_version}:{msg_num}".encode("utf-8")

        plaintext_bytes = aesgcm.decrypt(nonce, ciphertext_and_tag, aad)
        bob_last_seen_msg_num = msg_num
        return plaintext_bytes.decode("utf-8")

    # 1. Alice envía el Mensaje #1
    print("\n[1] Alice envía mensaje legítimo #1 a Bob:")
    msg1_text = "Transferir $50 a David (Transacción 101)"
    msg1_nonce = os.urandom(12)
    msg1_aad = f"{sender_id}:{recipient_id}:{protocol_version}:1".encode("utf-8")
    msg1_wire = b64url_encode(msg1_nonce + aesgcm.encrypt(msg1_nonce, msg1_text.encode("utf-8"), msg1_aad))

    bob_res1 = bob_receive(msg1_wire, msg_num=1)
    print(f"  * Bob procesa Mensaje #1 : '{bob_res1}'")
    print(f"  * Estado de Bob          : last_seen_msg_num = {bob_last_seen_msg_num}")

    # 2. Alice envía el Mensaje #2
    print("\n[2] Alice envía mensaje legítimo #2 a Bob:")
    msg2_text = "Transferir $20 a David (Transacción 102)"
    msg2_nonce = os.urandom(12)
    msg2_aad = f"{sender_id}:{recipient_id}:{protocol_version}:2".encode("utf-8")
    msg2_wire = b64url_encode(msg2_nonce + aesgcm.encrypt(msg2_nonce, msg2_text.encode("utf-8"), msg2_aad))

    bob_res2 = bob_receive(msg2_wire, msg_num=2)
    print(f"  * Bob procesa Mensaje #2 : '{bob_res2}'")
    print(f"  * Estado de Bob          : last_seen_msg_num = {bob_last_seen_msg_num}")

    # 3. Ataque A: Reinyectar el Mensaje #1 capturado
    print("\n[3] ATACANTE reinyecta el Mensaje #1 capturado previamente (Replay directo):")
    try:
        bob_receive(msg1_wire, msg_num=1)
        print("❌ FALLO DE SEGURIDAD: El mensaje repetido fue aceptado.")
        sys.exit(1)
    except ValueError as e:
        print("✅ ATAQUE DETENIDO CON ÉXITO:")
        print(f"  * {e}")
        print("  * El cliente detectó que el número de secuencia no es monotónicamente creciente.")
        print("  * Consecuencia: Mensaje duplicado descartado sin procesar la transacción.")

    # 4. Ataque B: Atacante intenta engañar al contador cambiando msg_num a 3
    print("\n[4] ATACANTE intenta engañar a Bob cambiando msg_num a 3 con el ciphertext viejo:")
    try:
        bob_receive(msg1_wire, msg_num=3)
        print("❌ FALLO DE SEGURIDAD: El atacante eludió el contador modificando la metadata.")
        sys.exit(1)
    except InvalidTag:
        print("✅ ATAQUE DETENIDO CON ÉXITO:")
        print("  * La verificación del Tag AEAD falló: InvalidTag")
        print("  * Razón: msg_num forma parte obligatoria de los Datos Asociados (AAD) autenticados.")
        print("  * Consecuencia: El atacante no puede alterar la secuencia sin invalidar la firma GCM.")
    print("=" * 70)


if __name__ == "__main__":
    main()
