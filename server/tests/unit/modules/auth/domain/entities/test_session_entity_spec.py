from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from uuid import uuid4
import pytest

from app.modules.auth.domain.entities.session_entity import SessionEntity


def test_session_entity_creation():
    """
    ↳ SessionEntity: almacena identidad de sesion y estado activo
    """
    sid = uuid4()
    uid = uuid4()
    now = datetime.now(timezone.utc)
    sess = SessionEntity(
        id=sid,
        user_id=uid,
        token_hash="hash_123",
        expires_at=now,
        revoked_at=None,
        created_at=now,
    )
    assert sess.id == sid
    assert sess.user_id == uid
    assert sess.token_hash == "hash_123"
    assert sess.revoked_at is None


def test_session_entity_create_factory():
    """
    ↳ SessionEntity: metodo fabrica create genera id, revoked_at vacio y timestamp actual
    """
    uid = uuid4()
    exp = datetime.now(timezone.utc)
    sess = SessionEntity.create(
        user_id=uid,
        token_hash="hash_123",
        expires_at=exp,
    )
    assert sess.id is not None
    assert sess.user_id == uid
    assert sess.token_hash == "hash_123"
    assert sess.expires_at == exp
    assert sess.revoked_at is None
    assert sess.created_at is not None


def test_session_entity_immutable():
    """
    ↳ SessionEntity: es inmutable al ser frozen dataclass
    """
    sess = SessionEntity(
        id=uuid4(),
        user_id=uuid4(),
        token_hash="hash",
        expires_at=datetime.now(timezone.utc),
        revoked_at=None,
        created_at=datetime.now(timezone.utc),
    )
    with pytest.raises(FrozenInstanceError):
        sess.revoked_at = datetime.now(timezone.utc)
