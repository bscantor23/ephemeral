from datetime import datetime, timezone
from uuid import uuid4

import app.commons.db.all_models
from app.commons.db.base import Base
from app.commons.db.schemas.message_schema import MessageSchema
from app.commons.db.schemas.prekey_bundle_schema import PrekeyBundleSchema
from app.commons.db.schemas.session_schema import SessionSchema
from app.commons.db.schemas.user_schema import UserSchema


def test_schemas_registered_in_metadata():
    """
    ↳ Schemas: Base.metadata registra las 4 tablas del sistema
    """
    tables = Base.metadata.tables.keys()
    assert "users" in tables
    assert "sessions" in tables
    assert "prekey_bundles" in tables
    assert "messages" in tables


def test_schema_entities_instantiable():
    """
    ↳ Schemas: modelos ORM instanciables con atributos esperados
    """
    now = datetime.now(timezone.utc)
    uid = uuid4()
    user = UserSchema(
        id=uid,
        username="alice",
        display_name="Alice",
        password_hash="hash",
        identity_sign_pub="sp",
        identity_dh_pub="dp",
        identity_dh_sig="ds",
        created_at=now,
        updated_at=now,
    )
    assert user.id == uid
    assert user.username == "alice"

    sess = SessionSchema(
        id=uuid4(),
        user_id=uid,
        token_hash="th",
        expires_at=now,
        revoked_at=None,
        created_at=now,
    )
    assert sess.user_id == uid

    bundle = PrekeyBundleSchema(
        id=uuid4(),
        user_id=uid,
        signed_prekey_pub="pk",
        signature="sig",
        is_active=True,
        created_at=now,
        expires_at=now,
    )
    assert bundle.signature == "sig"

    msg = MessageSchema(
        id=uuid4(),
        chat_session_id=uuid4(),
        sender_id=uid,
        recipient_id=uuid4(),
        protocol_version=1,
        msg_num=1,
        ephemeral_pub="ephem",
        signed_prekey_id=bundle.id,
        ciphertext="encrypted_payload",
        delivered_at=None,
        created_at=now,
    )
    assert msg.msg_num == 1
