from datetime import datetime, timezone
from unittest.mock import MagicMock
from uuid import uuid4

from app.commons.db.schemas.message_schema import MessageSchema
from app.modules.messages.domain.entities.message_entity import MessageEntity
from app.modules.messages.infrastructure.outbound.persistence.repositories.postgres_message_repository import (
    PostgresMessageRepository,
)


def _make_mock_session_factory(session_mock):
    def factory():
        yield session_mock

    return factory


def test_postgres_message_repo_save():
    """
    ↳ save persiste el schema y retorna entity
    """
    session = MagicMock()
    repo = PostgresMessageRepository(session_factory=_make_mock_session_factory(session))

    entity = MessageEntity.create(
        chat_session_id=uuid4(),
        sender_id=uuid4(),
        recipient_id=uuid4(),
        msg_num=0,
        ciphertext="enc_data",
    )

    saved = repo.save(entity)
    assert saved.id == entity.id
    session.add.assert_called_once()
    session.commit.assert_called_once()


def test_postgres_message_repo_get_by_id():
    """
    ↳ get_by_id retorna entity si existe o None si no
    """
    session = MagicMock()
    mid = uuid4()
    now = datetime.now(timezone.utc)
    schema = MessageSchema(
        id=mid,
        chat_session_id=uuid4(),
        sender_id=uuid4(),
        recipient_id=uuid4(),
        protocol_version=1,
        msg_num=0,
        ciphertext="enc",
        ephemeral_pub=None,
        signed_prekey_id=None,
        delivered_at=None,
        created_at=now,
    )

    session.scalar.side_effect = [schema, None]
    repo = PostgresMessageRepository(session_factory=_make_mock_session_factory(session))

    assert repo.get_by_id(mid) is not None
    assert repo.get_by_id(uuid4()) is None


def test_postgres_message_repo_get_pending_by_recipient():
    """
    ↳ get_pending_by_recipient retorna lista de entities pendientes
    """
    session = MagicMock()
    now = datetime.now(timezone.utc)
    s1 = MessageSchema(
        id=uuid4(),
        chat_session_id=uuid4(),
        sender_id=uuid4(),
        recipient_id=uuid4(),
        protocol_version=1,
        msg_num=0,
        ciphertext="m1",
        ephemeral_pub=None,
        signed_prekey_id=None,
        delivered_at=None,
        created_at=now,
    )
    scalars_mock = MagicMock()
    scalars_mock.all.return_value = [s1]
    session.scalars.return_value = scalars_mock

    repo = PostgresMessageRepository(session_factory=_make_mock_session_factory(session))
    pending = repo.get_pending_by_recipient(uuid4(), limit=10)

    assert len(pending) == 1
    assert pending[0].ciphertext == "m1"


def test_postgres_message_repo_mark_delivered():
    """
    ↳ mark_delivered actualiza delivered_at
    """
    session = MagicMock()
    mid = uuid4()
    now = datetime.now(timezone.utc)
    schema = MessageSchema(
        id=mid,
        chat_session_id=uuid4(),
        sender_id=uuid4(),
        recipient_id=uuid4(),
        protocol_version=1,
        msg_num=0,
        ciphertext="m1",
        ephemeral_pub=None,
        signed_prekey_id=None,
        delivered_at=None,
        created_at=now,
    )
    session.scalar.side_effect = [schema, None]

    repo = PostgresMessageRepository(session_factory=_make_mock_session_factory(session))
    updated = repo.mark_delivered(mid, now)

    assert updated is not None
    assert updated.delivered_at == now
    assert repo.mark_delivered(uuid4(), now) is None


def test_postgres_message_repo_delete_delivered_before():
    """
    ↳ delete_delivered_before ejecuta DELETE y retorna rowcount
    """
    session = MagicMock()
    mock_result = MagicMock()
    mock_result.rowcount = 4
    session.execute.return_value = mock_result

    repo = PostgresMessageRepository(
        session_factory=_make_mock_session_factory(session)
    )
    count = repo.delete_delivered_before(datetime.now(timezone.utc))

    assert count == 4
    session.execute.assert_called_once()
    session.commit.assert_called_once()
