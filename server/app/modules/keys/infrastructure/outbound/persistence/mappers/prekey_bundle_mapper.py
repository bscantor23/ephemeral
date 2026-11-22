from app.commons.db.schemas.prekey_bundle_schema import PrekeyBundleSchema
from app.modules.keys.domain.entities.prekey_bundle_entity import (
    PrekeyBundleEntity,
)


class PrekeyBundleMapper:
    @staticmethod
    def to_entity(schema: PrekeyBundleSchema) -> PrekeyBundleEntity:
        return PrekeyBundleEntity(
            id=schema.id,
            user_id=schema.user_id,
            signed_prekey_pub=schema.signed_prekey_pub,
            signature=schema.signature,
            is_active=schema.is_active,
            created_at=schema.created_at,
            expires_at=schema.expires_at,
        )

    @staticmethod
    def to_schema(entity: PrekeyBundleEntity) -> PrekeyBundleSchema:
        return PrekeyBundleSchema(
            id=entity.id,
            user_id=entity.user_id,
            signed_prekey_pub=entity.signed_prekey_pub,
            signature=entity.signature,
            is_active=entity.is_active,
            created_at=entity.created_at,
            expires_at=entity.expires_at,
        )
