from app.commons.db.schemas.session_schema import SessionSchema
from app.modules.auth.domain.entities.session_entity import SessionEntity


class SessionMapper:
    @staticmethod
    def to_entity(schema: SessionSchema) -> SessionEntity:
        return SessionEntity(
            id=schema.id,
            user_id=schema.user_id,
            token_hash=schema.token_hash,
            expires_at=schema.expires_at,
            revoked_at=schema.revoked_at,
            created_at=schema.created_at,
        )

    @staticmethod
    def to_schema(entity: SessionEntity) -> SessionSchema:
        return SessionSchema(
            id=entity.id,
            user_id=entity.user_id,
            token_hash=entity.token_hash,
            expires_at=entity.expires_at,
            revoked_at=entity.revoked_at,
            created_at=entity.created_at,
        )

    to_vo = to_entity
