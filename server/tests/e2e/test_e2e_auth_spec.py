from fastapi.testclient import TestClient

from tests.e2e.conftest import register_and_login_helper
from tests.helpers.crypto_fixtures import (
    build_register_payload,
    generate_client_identity,
)


def test_e2e_register_and_login_full_cycle(e2e_client: TestClient):
    """
    ↳ Registro de nuevo usuario con claves criptograficas validas, login exitoso y consulta a /auth/me
    """
    keys = generate_client_identity()
    user_data, token, _ = register_and_login_helper(
        e2e_client,
        username="alice",
        display_name="Alice Liddell",
        keys=keys,
    )

    assert user_data["username"] == "alice"
    assert user_data["display_name"] == "Alice Liddell"
    assert user_data["identity_sign_pub"] == keys.identity_sign_pub
    assert user_data["identity_dh_pub"] == keys.identity_dh_pub

    me_res = e2e_client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["id"] == user_data["id"]
    assert me_data["username"] == "alice"


def test_e2e_login_invalid_password_fails(e2e_client: TestClient):
    """
    ↳ Intento de login con contrasena incorrecta responde 401 Unauthorized
    """
    register_and_login_helper(e2e_client, username="bob", password="Password123!")

    bad_login_res = e2e_client.post(
        "/auth/login",
        json={"username": "bob", "password": "WrongPassword999!"},
    )
    assert bad_login_res.status_code == 401
    assert "Invalid username or password" in bad_login_res.json()["detail"]


def test_e2e_duplicate_registration_rejected(e2e_client: TestClient):
    """
    ↳ Intento de registro con nombre de usuario existente responde 409 Conflict
    """
    register_and_login_helper(e2e_client, username="charlie")

    dup_payload = build_register_payload(username="charlie")
    dup_res = e2e_client.post("/auth/register", json=dup_payload)
    assert dup_res.status_code == 409
    assert "already taken" in dup_res.json()["detail"]


def test_e2e_logout_revokes_session(e2e_client: TestClient):
    """
    ↳ Logout invalida la sesion activa y peticiones subsecuentes a /auth/me son rechazadas con 401
    """
    _, token, _ = register_and_login_helper(e2e_client, username="dave")

    pre_check = e2e_client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert pre_check.status_code == 200

    logout_res = e2e_client.post(
        "/auth/logout",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert logout_res.status_code == 204

    post_check = e2e_client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert post_check.status_code == 401


def test_e2e_unauthenticated_me_rejected(e2e_client: TestClient):
    """
    ↳ Consulta a /auth/me sin cabecera de autorizacion responde 401 Unauthorized
    """
    res = e2e_client.get("/auth/me")
    assert res.status_code == 401
