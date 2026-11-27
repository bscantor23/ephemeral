from uuid import uuid4
from fastapi.testclient import TestClient

from tests.e2e.conftest import register_and_login_helper
from tests.helpers.crypto_fixtures import (
    encrypt_message_aead,
    generate_client_identity,
    generate_signed_prekey,
    simulate_x3dh_initiator,
)


def test_e2e_send_and_receive_pending_messages(e2e_client: TestClient):
    """
    ↳ Envio de mensaje cifrado, recuperacion en bandeja de pendientes y confirmacion mediante ACK
    """
    bob_keys = generate_client_identity()
    bob, bob_token, _ = register_and_login_helper(
        e2e_client, username="bob_msg", keys=bob_keys
    )
    alice_keys = generate_client_identity()
    alice, alice_token, _ = register_and_login_helper(
        e2e_client, username="alice_msg", keys=alice_keys
    )

    spk = generate_signed_prekey(bob_keys)
    e2e_client.post(
        "/keys/prekey",
        json={
            "signed_prekey_pub": spk.prekey_pub_b64,
            "signature": spk.signature_b64,
        },
        headers={"Authorization": f"Bearer {bob_token}"},
    )

    bundle = e2e_client.get(
        f"/keys/{bob['id']}/bundle",
        headers={"Authorization": f"Bearer {alice_token}"},
    ).json()

    session_key, ek_b64 = simulate_x3dh_initiator(
        alice_keys=alice_keys,
        bob_identity_dh_pub_b64=bundle["identity_dh_pub"],
        bob_spk_pub_b64=bundle["signed_prekey_pub"],
    )

    ciphertext_b64 = encrypt_message_aead(
        plaintext="Hola Bob, mensaje offline seguro",
        session_key=session_key,
        sender_id=alice["id"],
        recipient_id=bob["id"],
        protocol_version=1,
        msg_num=1,
    )

    chat_session_id = str(uuid4())
    send_payload = {
        "recipient_id": bob["id"],
        "chat_session_id": chat_session_id,
        "ciphertext": ciphertext_b64,
        "ephemeral_pub": ek_b64,
        "msg_num": 1,
    }
    send_res = e2e_client.post(
        "/messages",
        json=send_payload,
        headers={"Authorization": f"Bearer {alice_token}"},
    )
    assert send_res.status_code == 201
    created_msg = send_res.json()
    assert created_msg["sender_id"] == alice["id"]
    assert created_msg["recipient_id"] == bob["id"]
    assert created_msg["delivered_at"] is None

    pending_res = e2e_client.get(
        "/messages/pending",
        headers={"Authorization": f"Bearer {bob_token}"},
    )
    assert pending_res.status_code == 200
    pending_data = pending_res.json()
    assert pending_data["count"] == 1
    assert len(pending_data["messages"]) == 1
    received = pending_data["messages"][0]
    assert received["id"] == created_msg["id"]
    assert received["ciphertext"] == ciphertext_b64

    ack_res = e2e_client.post(
        f"/messages/{received['id']}/ack",
        headers={"Authorization": f"Bearer {bob_token}"},
    )
    assert ack_res.status_code == 200
    assert ack_res.json()["delivered_at"] is not None

    pending_after = e2e_client.get(
        "/messages/pending",
        headers={"Authorization": f"Bearer {bob_token}"},
    ).json()
    assert pending_after["count"] == 0
    assert len(pending_after["messages"]) == 0


def test_e2e_acknowledge_forbidden_for_other_user(e2e_client: TestClient):
    """
    ↳ Intento de confirmar un mensaje por un usuario distinto al destinatario responde 403 Forbidden
    """
    bob, _, _ = register_and_login_helper(e2e_client, username="bob_forbid")
    alice, alice_token, _ = register_and_login_helper(e2e_client, username="alice_forbid")
    charlie, charlie_token, _ = register_and_login_helper(
        e2e_client, username="charlie_forbid"
    )

    send_res = e2e_client.post(
        "/messages",
        json={
            "recipient_id": bob["id"],
            "chat_session_id": str(uuid4()),
            "ciphertext": "dummy_ciphertext_base64",
            "ephemeral_pub": "dummy_ephemeral_key",
            "msg_num": 1,
        },
        headers={"Authorization": f"Bearer {alice_token}"},
    )
    assert send_res.status_code == 201
    msg_id = send_res.json()["id"]

    ack_charlie = e2e_client.post(
        f"/messages/{msg_id}/ack",
        headers={"Authorization": f"Bearer {charlie_token}"},
    )
    assert ack_charlie.status_code == 403


def test_e2e_websocket_realtime_delivery_and_ping_pong(e2e_client: TestClient):
    """
    ↳ Entrega en tiempo real via WebSocket cuando el destinatario esta conectado
    """
    bob, bob_token, _ = register_and_login_helper(e2e_client, username="bob_ws")
    alice, alice_token, _ = register_and_login_helper(e2e_client, username="alice_ws")

    with e2e_client.websocket_connect(f"/ws?token={bob_token}") as ws:
        ws.send_json({"type": "ping"})
        pong_data = ws.receive_json()
        assert pong_data == {"type": "pong"}

        send_res = e2e_client.post(
            "/messages",
            json={
                "recipient_id": bob["id"],
                "chat_session_id": str(uuid4()),
                "ciphertext": "realtime_ciphertext_payload",
                "ephemeral_pub": "realtime_ephemeral_key",
                "msg_num": 1,
            },
            headers={"Authorization": f"Bearer {alice_token}"},
        )
        assert send_res.status_code == 201
        msg_id = send_res.json()["id"]

        ws_event = ws.receive_json()
        assert ws_event["type"] == "message.incoming"
        assert ws_event["data"]["id"] == msg_id
        assert ws_event["data"]["ciphertext"] == "realtime_ciphertext_payload"
        assert ws_event["data"]["sender_id"] == alice["id"]

        ack_res = e2e_client.post(
            f"/messages/{msg_id}/ack",
            headers={"Authorization": f"Bearer {bob_token}"},
        )
        assert ack_res.status_code == 200
        assert ack_res.json()["delivered_at"] is not None
