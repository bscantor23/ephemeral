from datetime import datetime, timezone
from unittest.mock import MagicMock
from uuid import uuid4

from app.commons.db.schemas.user_schema import UserSchema
from app.modules.users.domain.value_objects.list_users_vo import ListUsersQueryVO
from app.modules.users.infrastructure.outbound.persistence.repositories.postgres_user_directory_repository import (
    PostgresUserDirectoryRepository,
)


def _make_mock_session_factory(session_mock):
    def factory():
        yield session_mock

    return factory


def test_postgres_user_directory_repo_get_by_id_found():
    """
    ↳ get_by_id retorna entidad con prekey activa si existe
    """
    uid = uuid4()
    now = datetime.now(timezone.utc)
    user_schema = UserSchema(
        id=uid,
        username="alice",
        display_name="Alice",
        password_hash="hash",
        identity_sign_pub="sig_pub",
        identity_dh_pub="dh_pub",
        identity_dh_sig="dh_sig",
        created_at=now,
        updated_at=now,
    )

    session = MagicMock()
    # first scalar call for UserSchema, second for prekey check
    session.scalar.side_effect = [user_schema, uuid4()]

    repo = PostgresUserDirectoryRepository(session_factory=_make_mock_session_factory(session))
    result = repo.get_by_id(uid)

    assert result is not None
    assert result.id == uid
    assert result.has_active_prekey is True


def test_postgres_user_directory_repo_get_by_id_none():
    """
    ↳ get_by_id retorna None si usuario no existe
    """
    session = MagicMock()
    session.scalar.return_value = None

    repo = PostgresUserDirectoryRepository(session_factory=_make_mock_session_factory(session))
    result = repo.get_by_id(uuid4())

    assert result is None


def test_postgres_user_directory_repo_get_by_username_found():
    """
    ↳ get_by_username retorna entidad con prekey inactiva si no tiene
    """
    uid = uuid4()
    now = datetime.now(timezone.utc)
    user_schema = UserSchema(
        id=uid,
        username="bob",
        display_name="Bob",
        password_hash="hash",
        identity_sign_pub="sig_bob",
        identity_dh_pub="dh_bob",
        identity_dh_sig="dh_sig",
        created_at=now,
        updated_at=now,
    )

    session = MagicMock()
    # first scalar call for UserSchema, second for prekey check (None)
    session.scalar.side_effect = [user_schema, None]

    repo = PostgresUserDirectoryRepository(session_factory=_make_mock_session_factory(session))
    result = repo.get_by_username("bob")

    assert result is not None
    assert result.username == "bob"
    assert result.has_active_prekey is False


def test_postgres_user_directory_repo_get_by_username_none():
    """
    ↳ get_by_username retorna None si no existe
    """
    session = MagicMock()
    session.scalar.return_value = None

    repo = PostgresUserDirectoryRepository(session_factory=_make_mock_session_factory(session))
    result = repo.get_by_username("nobody")

    assert result is None


def test_postgres_user_directory_repo_list_users():
    """
    ↳ list_users pagina, filtra y marca prekeys en lote
    """
    uid1 = uuid4()
    uid2 = uuid4()
    now = datetime.now(timezone.utc)
    u1 = UserSchema(
        id=uid1,
        username="alice",
        display_name="Alice",
        password_hash="hash",
        identity_sign_pub="sig1",
        identity_dh_pub="dh1",
        identity_dh_sig="sig1",
        created_at=now,
        updated_at=now,
    )
    u2 = UserSchema(
        id=uid2,
        username="bob",
        display_name="Bob",
        password_hash="hash",
        identity_sign_pub="sig2",
        identity_dh_pub="dh2",
        identity_dh_sig="sig2",
        created_at=now,
        updated_at=now,
    )

    session = MagicMock()
    # total count scalar
    session.scalar.return_value = 2

    scalars_mock = MagicMock()
    # first scalars().all() returns users list, second returns active prekey user_ids
    scalars_mock.all.side_effect = [[u1, u2], [uid1]]
    session.scalars.return_value = scalars_mock

    repo = PostgresUserDirectoryRepository(session_factory=_make_mock_session_factory(session))
    query = ListUsersQueryVO(search="al", limit=10, offset=0, exclude_user_id=uuid4())
    entities, total = repo.list_users(query)

    assert total == 2
    assert len(entities) == 2
    assert entities[0].id == uid1
    assert entities[0].has_active_prekey is True
    assert entities[1].id == uid2
    assert entities[1].has_active_prekey is False


def test_postgres_user_directory_repo_list_users_empty():
    """
    ↳ list_users maneja lista vacia sin llamar consulta de prekeys
    """
    session = MagicMock()
    session.scalar.return_value = 0

    scalars_mock = MagicMock()
    scalars_mock.all.return_value = []
    session.scalars.return_value = scalars_mock

    repo = PostgresUserDirectoryRepository(session_factory=_make_mock_session_factory(session))
    query = ListUsersQueryVO(search=None, limit=10, offset=0, exclude_user_id=None)
    entities, total = repo.list_users(query)

    assert total == 0
    assert len(entities) == 0
