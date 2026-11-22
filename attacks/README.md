# Scripts de Ataque y Evidencias Red Team (E5) — UD-Chat E2EE

Este directorio contiene las pruebas de concepto reproducibles de los ataques definidos en la sección **5.5 del enunciado** y el documento **E1**:

| ID | Ataque Demostrado | Mecanismo de Defensa que lo Detiene | Script |
|:---|:---|:---|:---|
| **A1** | El servidor sustituye la *signed prekey* de Bob (MITM) | Verificación de firma ECDSA P-256 en el cliente receptor | `attack_a1_swap_spk.py` |
| **A2** | El servidor sustituye la clave de identidad de Bob | Cambio del *Safety Number* (SHA-512) y alerta visible | `attack_a2_swap_identity.py` |

---

## Cómo Ejecutar los Ataques

Con los servicios levantados (`docker compose up`):

```bash
# Ataque A1: Sustitución de Signed Prekey
python3 attacks/attack_a1_swap_spk.py

# Ataque A2: Sustitución de Clave de Identidad
python3 attacks/attack_a2_swap_identity.py
```
