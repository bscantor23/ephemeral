from datetime import datetime, timedelta, timezone
from uuid import uuid4
import pytest

from app.commons.errors.base_errors import DomainError
from app.modules.auth.domain.entities.session_entity import SessionEntity
from app.modules.auth.domain.errors.auth_errors import SessionExpiredError
from app.modules.auth.domain.rules.auth_rules import AuthRules


def test_normalize_valid_username():
    """
    ↳ Reglas: normaliza username a minusculas y sin espacios
    """
    assert AuthRules.normalize_username("  Alice_01  ") == "alice_01"


def test_normalize_invalid_short_username():
    """
    ↳ Reglas: username menor a 3 caracteres lanza DomainError
    """
    with pytest.raises(DomainError):
        AuthRules.normalize_username("al")


def test_normalize_invalid_characters():
    """
    ↳ Reglas: caracteres no permitidos en username lanza DomainError
    """
    with pytest.raises(DomainError):
        AuthRules.normalize_username("alice@home")


def test_validate_session_active_success():
    """
    ↳ Reglas: sesion vigente y no revocada pasa validacion
    """
    session = SessionEntity(
        id=uuid4(),
        user_id=uuid4(),
        token_hash="hash",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=30),
        revoked_at=None,
        created_at=datetime.now(timezone.utc),
    )
    AuthRules.validate_session_active(session)


def test_validate_session_revoked():
    """
    ↳ Reglas: sesion con fecha de revocacion lanza SessionExpiredError
    """
    session = SessionEntity(
        id=uuid4(),
        user_id=uuid4(),
        token_hash="hash",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=30),
        revoked_at=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc),
    )
    with pytest.raises(SessionExpiredError):
        AuthRules.validate_session_active(session)


def test_validate_session_expired():
    """
    ↳ Reglas: sesion con expires_at en el pasado lanza SessionExpiredError
    """
    session = SessionEntity(
        id=uuid4(),
        user_id=uuid4(),
        token_hash="hash",
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=5),
        revoked_at=None,
        created_at=datetime.now(timezone.utc) - timedelta(minutes=65),
    )
    with pytest.raises(SessionExpiredError):
        AuthRules.validate_session_active(session)
