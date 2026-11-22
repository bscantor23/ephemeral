#!/usr/bin/env python3
"""
Demostración de Ataque A2 — Sustitución de Clave de Identidad (MITM Total).
Evaluación: Sección 5.5 del enunciado / Hito E5.

Escenario:
  1. Si el servidor sustituye tanto la Prekey como la Clave de Identidad de Bob por claves
     creadas por el servidor (con firmas válidas entre sí), la firma criptográfica pasaría.
  2. DEFENSA: El protocolo Signal / UD-Chat utiliza "Safety Numbers" (números de seguridad o huellas).
  3. Alice y Bob tienen un canal fuera de banda (código QR o huella comparada en persona).
  4. Cuando el servidor altera la clave de identidad, el Safety Number cambia drásticamente.

Resultado Esperado:
  El Safety Number calculado no coincide con el verificado previamente.
  El cliente detecta el cambio de identidad, emite una alerta crítica y bloquea el chat.
"""

import hashlib
import sys
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat


def calculate_safety_number(pub1: bytes, pub2: bytes) -> str:
    """
    Calcula el Safety Number de 60 dígitos mediante SHA-512
    de las claves públicas ordenadas lexicográficamente (formato Signal).
    """
    sorted_keys = sorted([pub1, pub2])
    digest = hashlib.sha512(sorted_keys[0] + sorted_keys[1]).digest()
    # Extraer bloques numéricos de 5 dígitos
    numbers = []
    for i in range(0, 30, 2):
        chunk = int.from_bytes(digest[i:i+2], "big") % 100000
        numbers.append(f"{chunk:05d}")
    return " ".join(numbers[:12])  # 60 dígitos en 12 bloques de 5


def main():
    print("=" * 70)
    print("DEMOSTRACIÓN DE ATAQUE A2: Sustitución de Identidad y Safety Number")
    print("=" * 70)

    # 1. Claves legítimas de Alice y Bob
    alice_priv = ec.generate_private_key(ec.SECP256R1())
    alice_pub = alice_priv.public_key().public_bytes(Encoding.X962, PublicFormat.UncompressedPoint)

    bob_priv = ec.generate_private_key(ec.SECP256R1())
    bob_pub = bob_priv.public_key().public_bytes(Encoding.X962, PublicFormat.UncompressedPoint)

    legitimate_safety_number = calculate_safety_number(alice_pub, bob_pub)
    print("\n[1] Identidades legítimas:")
    print(f"  * Safety Number Original (Alice <-> Bob):")
    print(f"    {legitimate_safety_number}")

    # 2. El Atacante sustituye la clave de identidad de Bob en el servidor
    print("\n[2] ATACANTE sustituye la identidad de Bob en el servidor (swap_identity):")
    attacker_priv = ec.generate_private_key(ec.SECP256R1())
    attacker_pub = attacker_priv.public_key().public_bytes(Encoding.X962, PublicFormat.UncompressedPoint)

    # 3. Alice recalcula el Safety Number con la identidad recibida del servidor
    tampered_safety_number = calculate_safety_number(alice_pub, attacker_pub)
    print(f"  * Safety Number con identidad sustituida:")
    print(f"    {tampered_safety_number}")

    # 4. Verificación de Detección
    print("\n[3] Verificación del mecanismo de defensa:")
    if legitimate_safety_number != tampered_safety_number:
        print("✅ ATAQUE DETENIDO CON ÉXITO:")
        print("  * Los Safety Numbers NO coinciden.")
        print("  * La aplicación del usuario detecta: 'La clave de identidad del contacto ha cambiado'.")
        print("  * Consecuencia: Se bloquea la comunicación hasta verificar de nuevo el código QR.")
    else:
        print("❌ FALLO DE SEGURIDAD: Los números de seguridad coincidieron.")
        sys.exit(1)
    print("=" * 70)


if __name__ == "__main__":
    main()
