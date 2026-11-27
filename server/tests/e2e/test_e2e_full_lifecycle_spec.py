from uuid import uuid4
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature
from fastapi.testclient import TestClient

from tests.e2e.conftest import register_and_login_helper
from tests.helpers.crypto_fixtures import (
    _b64url_decode,
    calculate_safety_number,
    decrypt_message_aead,
    encrypt_message_aead,
    generate_client_identity,
    generate_signed_prekey,
    simulate_x3dh_initiator,
    simulate_x3dh_receiver,
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


def test_e2e_full_alice_bob_cryptographic_messaging_lifecycle(
    e2e_client: TestClient,
):
    """
    ↳ Ciclo completo E2E: registro, publicacion de prekeys, descubrimiento, X3DH, intercambio de mensajes cifrados AEAD en tiempo real y offline, ACKs y verificacion de Safety Number
    """
    # 1. Generación de claves de identidad locales para Alice y Bob
    alice_keys = generate_client_identity()
    bob_keys = generate_client_identity()

    # 2. Registro y login en el servidor
    bob_user, bob_token, _ = register_and_login_helper(
        e2e_client,
        username="bob_lifecycle",
        display_name="Bob Security",
        keys=bob_keys,
    )
    alice_user, alice_token, _ = register_and_login_helper(
        e2e_client,
        username="alice_lifecycle",
        display_name="Alice Security",
        keys=alice_keys,
    )

    # 3. Bob publica su Signed Prekey (SPK) firmada localmente
    bob_spk = generate_signed_prekey(bob_keys)
    spk_upload_res = e2e_client.post(
        "/keys/prekey",
        json={
            "signed_prekey_pub": bob_spk.prekey_pub_b64,
            "signature": bob_spk.signature_b64,
        },
        headers={"Authorization": f"Bearer {bob_token}"},
    )
    assert spk_upload_res.status_code == 201

    # 4. Alice descubre a Bob en el directorio y descarga su bundle criptográfico
    dir_res = e2e_client.get(
        "/users",
        params={"limit": 10},
        headers={"Authorization": f"Bearer {alice_token}"},
    )
    assert dir_res.status_code == 200
    found_bob = next(
        u for u in dir_res.json()["users"] if u["username"] == "bob_lifecycle"
    )
    assert found_bob["id"] == bob_user["id"]

    bundle_res = e2e_client.get(
        f"/keys/{bob_user['id']}/bundle",
        headers={"Authorization": f"Bearer {alice_token}"},
    )
    assert bundle_res.status_code == 200
    bob_bundle = bundle_res.json()

    # 5. Alice verifica criptográficamente la firma de la SPK de Bob
    assert _verify_spk_signature(
        identity_sign_pub_b64=bob_bundle["identity_sign_pub"],
        signed_prekey_pub_b64=bob_bundle["signed_prekey_pub"],
        signature_b64=bob_bundle["signature"],
    )

    # 6. Alice ejecuta X3DH Initiator y deriva clave de sesión K
    alice_session_key, alice_ek_pub_b64 = simulate_x3dh_initiator(
        alice_keys=alice_keys,
        bob_identity_dh_pub_b64=bob_bundle["identity_dh_pub"],
        bob_spk_pub_b64=bob_bundle["signed_prekey_pub"],
    )

    chat_session_id = str(uuid4())

    # 7. Bob abre canal WebSocket en tiempo real
    with e2e_client.websocket_connect(f"/ws?token={bob_token}") as bob_ws:
        bob_ws.send_json({"type": "ping"})
        assert bob_ws.receive_json() == {"type": "pong"}

        # 8. Alice cifra Mensaje #1 con AES-256-GCM y lo envía por la API
        msg1_plaintext = "Hola Bob! Mensaje confidencial en tiempo real via UD-Chat."
        msg1_ciphertext = encrypt_message_aead(
            plaintext=msg1_plaintext,
            session_key=alice_session_key,
            sender_id=alice_user["id"],
            recipient_id=bob_user["id"],
            protocol_version=1,
            msg_num=1,
        )

        send_res1 = e2e_client.post(
            "/messages",
            json={
                "recipient_id": bob_user["id"],
                "chat_session_id": chat_session_id,
                "ciphertext": msg1_ciphertext,
                "ephemeral_pub": alice_ek_pub_b64,
                "msg_num": 1,
            },
            headers={"Authorization": f"Bearer {alice_token}"},
        )
        assert send_res1.status_code == 201
        msg1_id = send_res1.json()["id"]

        # 9. Bob recibe el mensaje #1 instantáneamente por WebSocket
        ws_event = bob_ws.receive_json()
        assert ws_event["type"] == "message.incoming"
        received_msg1 = ws_event["data"]
        assert received_msg1["id"] == msg1_id
        assert received_msg1["sender_id"] == alice_user["id"]

        # 10. Bob ejecuta X3DH Receiver y reconstruye la misma clave de sesión
        bob_session_key = simulate_x3dh_receiver(
            bob_keys=bob_keys,
            bob_spk=bob_spk,
            alice_identity_dh_pub_b64=alice_keys.identity_dh_pub,
            alice_ephemeral_pub_b64=received_msg1["ephemeral_pub"],
        )
        assert bob_session_key == alice_session_key

        # 11. Bob descifra el Mensaje #1 con éxito
        decrypted1 = decrypt_message_aead(
            ciphertext_b64=received_msg1["ciphertext"],
            session_key=bob_session_key,
            sender_id=alice_user["id"],
            recipient_id=bob_user["id"],
            protocol_version=1,
            msg_num=1,
        )
        assert decrypted1 == msg1_plaintext

        # 12. Bob confirma el mensaje con ACK
        ack_res1 = e2e_client.post(
            f"/messages/{msg1_id}/ack",
            headers={"Authorization": f"Bearer {bob_token}"},
        )
        assert ack_res1.status_code == 200
        assert ack_res1.json()["delivered_at"] is not None

    # 13. Bob está desconectado (fuera de línea). Alice envía Mensaje #2
    msg2_plaintext = "Bob, este es un segundo mensaje depositado mientras estabas offline."
    msg2_ciphertext = encrypt_message_aead(
        plaintext=msg2_plaintext,
        session_key=alice_session_key,
        sender_id=alice_user["id"],
        recipient_id=bob_user["id"],
        protocol_version=1,
        msg_num=2,
    )

    send_res2 = e2e_client.post(
        "/messages",
        json={
            "recipient_id": bob_user["id"],
            "chat_session_id": chat_session_id,
            "ciphertext": msg2_ciphertext,
            "ephemeral_pub": alice_ek_pub_b64,
            "msg_num": 2,
        },
        headers={"Authorization": f"Bearer {alice_token}"},
    )
    assert send_res2.status_code == 201
    msg2_id = send_res2.json()["id"]

    # 14. Bob vuelve a conectarse y consulta mensajes pendientes
    pending_res = e2e_client.get(
        "/messages/pending",
        headers={"Authorization": f"Bearer {bob_token}"},
    )
    assert pending_res.status_code == 200
    pending_data = pending_res.json()
    assert pending_data["count"] == 1
    offline_msg = pending_data["messages"][0]
    assert offline_msg["id"] == msg2_id

    # 15. Bob descifra el Mensaje #2 y envía ACK
    decrypted2 = decrypt_message_aead(
        ciphertext_b64=offline_msg["ciphertext"],
        session_key=bob_session_key,
        sender_id=alice_user["id"],
        recipient_id=bob_user["id"],
        protocol_version=1,
        msg_num=2,
    )
    assert decrypted2 == msg2_plaintext

    ack_res2 = e2e_client.post(
        f"/messages/{msg2_id}/ack",
        headers={"Authorization": f"Bearer {bob_token}"},
    )
    assert ack_res2.status_code == 200
    assert ack_res2.json()["delivered_at"] is not None

    # 16. Verificación de que la bandeja de pendientes queda vacía
    pending_empty = e2e_client.get(
        "/messages/pending",
        headers={"Authorization": f"Bearer {bob_token}"},
    ).json()
    assert pending_empty["count"] == 0

    # 17. Verificación del Safety Number (Alice y Bob comparan dígitos)
    alice_safety_number = calculate_safety_number(
        alice_keys._dh_pub_raw, bob_keys._dh_pub_raw
    )
    bob_safety_number = calculate_safety_number(
        bob_keys._dh_pub_raw, alice_keys._dh_pub_raw
    )
    assert alice_safety_number == bob_safety_number
    assert len(alice_safety_number.split()) == 12
