from app.commons.db.schemas.user_schema import UserSchema
from app.modules.auth.domain.entities.user_entity import UserEntity


class UserMapper:
    @staticmethod
    def to_entity(schema: UserSchema) -> UserEntity:
        return UserEntity(
            id=schema.id,
            username=schema.username,
            display_name=schema.display_name,
            password_hash=schema.password_hash,
            identity_sign_pub=schema.identity_sign_pub,
            identity_dh_pub=schema.identity_dh_pub,
            identity_dh_sig=schema.identity_dh_sig,
            created_at=schema.created_at,
            updated_at=schema.updated_at,
        )

    @staticmethod
    def to_schema(entity: UserEntity) -> UserSchema:
        return UserSchema(
            id=entity.id,
            username=entity.username,
            display_name=entity.display_name,
            password_hash=entity.password_hash,
            identity_sign_pub=entity.identity_sign_pub,
            identity_dh_pub=entity.identity_dh_pub,
            identity_dh_sig=entity.identity_dh_sig,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    to_vo = to_entity
