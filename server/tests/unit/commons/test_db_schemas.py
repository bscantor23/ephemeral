from app.commons.db.all_models import (
    Base,
    MessageSchema,
    PrekeyBundleSchema,
    SessionSchema,
    UserSchema,
)


def test_schemas_registered_in_metadata():
    """Schemas: Base.metadata registra las 4 tablas del sistema"""
    table_names = set(Base.metadata.tables.keys())
    assert {"users", "sessions", "prekey_bundles", "messages"}.issubset(table_names)


def test_schema_entities_instantiable():
    """Schemas: modelos ORM instanciables con atributos esperados"""
    user = UserSchema(
        username="alice",
        display_name="Alice",
        password_hash="hash",
        identity_sign_pub="sign_pub",
        identity_dh_pub="dh_pub",
        identity_dh_sig="dh_sig",
    )
    assert user.username == "alice"

    session = SessionSchema(token_hash="hash")
    assert session.token_hash == "hash"

    bundle = PrekeyBundleSchema(signed_prekey_pub="spk", signature="sig")
    assert bundle.signed_prekey_pub == "spk"

    message = MessageSchema(msg_num=0, ciphertext="cipher")
    assert message.msg_num == 0
