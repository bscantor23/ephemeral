from uuid import uuid4
from fastapi.testclient import TestClient

from tests.e2e.conftest import register_and_login_helper


def test_e2e_list_users_directory_with_pagination(e2e_client: TestClient):
    """
    ↳ Directorio de usuarios permite paginacion y busqueda excluyendo al usuario solicitante
    """
    alice, alice_token, _ = register_and_login_helper(e2e_client, username="alice_dir")
    bob, _, _ = register_and_login_helper(e2e_client, username="bob_dir")
    charlie, _, _ = register_and_login_helper(e2e_client, username="charlie_dir")

    res = e2e_client.get(
        "/users",
        params={"limit": 10, "offset": 0},
        headers={"Authorization": f"Bearer {alice_token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "users" in data
    assert data["total"] == 2
    returned_usernames = [u["username"] for u in data["users"]]
    assert "alice_dir" not in returned_usernames
    assert "bob_dir" in returned_usernames
    assert "charlie_dir" in returned_usernames


def test_e2e_get_user_by_username_success(e2e_client: TestClient):
    """
    ↳ Consulta de usuario por username devuelve perfil publico con claves de identidad
    """
    alice, alice_token, _ = register_and_login_helper(e2e_client, username="alice_find")
    bob, _, bob_keys = register_and_login_helper(e2e_client, username="bob_find")

    res = e2e_client.get(
        "/users/by-username/bob_find",
        headers={"Authorization": f"Bearer {alice_token}"},
    )
    assert res.status_code == 200
    user_info = res.json()
    assert user_info["id"] == bob["id"]
    assert user_info["username"] == "bob_find"
    assert user_info["identity_sign_pub"] == bob_keys.identity_sign_pub
    assert user_info["identity_dh_pub"] == bob_keys.identity_dh_pub


def test_e2e_get_user_by_id_success(e2e_client: TestClient):
    """
    ↳ Consulta de usuario por ID devuelve perfil publico con claves de identidad
    """
    _, alice_token, _ = register_and_login_helper(e2e_client, username="alice_byid")
    bob, _, bob_keys = register_and_login_helper(e2e_client, username="bob_byid")

    res = e2e_client.get(
        f"/users/{bob['id']}",
        headers={"Authorization": f"Bearer {alice_token}"},
    )
    assert res.status_code == 200
    user_info = res.json()
    assert user_info["id"] == bob["id"]
    assert user_info["username"] == "bob_byid"


def test_e2e_get_nonexistent_user_returns_404(e2e_client: TestClient):
    """
    ↳ Consulta de usuario inexistente por ID o username responde 404 Not Found
    """
    _, token, _ = register_and_login_helper(e2e_client, username="searcher_404")

    by_username = e2e_client.get(
        "/users/by-username/nonexistent_user",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert by_username.status_code == 404

    by_id = e2e_client.get(
        f"/users/{uuid4()}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert by_id.status_code == 404


def test_e2e_users_endpoints_require_authentication(e2e_client: TestClient):
    """
    ↳ Endpoints de usuarios sin token responden 401 Unauthorized
    """
    assert e2e_client.get("/users").status_code == 401
    assert e2e_client.get("/users/by-username/someuser").status_code == 401
    assert e2e_client.get(f"/users/{uuid4()}").status_code == 401
