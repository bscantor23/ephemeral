from app.commons.db.schemas.user_schema import UserSchema
from app.modules.users.domain.entities.user_profile_entity import UserProfileEntity
from app.modules.users.domain.value_objects.user_profile_vo import UserProfileVO
from app.modules.users.infrastructure.inbound.http.dto.user_profile_dto import (
    UserProfileResponseDTO,
)


class UserProfileMapper:
    @staticmethod
    def to_entity(user_schema: UserSchema, has_active_prekey: bool) -> UserProfileEntity:
        return UserProfileEntity(
            id=user_schema.id,
            username=user_schema.username,
            display_name=user_schema.display_name,
            identity_sign_pub=user_schema.identity_sign_pub,
            identity_dh_pub=user_schema.identity_dh_pub,
            has_active_prekey=has_active_prekey,
            created_at=user_schema.created_at,
        )

    @staticmethod
    def to_dto(vo: UserProfileVO) -> UserProfileResponseDTO:
        return UserProfileResponseDTO(
            id=vo.id,
            username=vo.username,
            display_name=vo.display_name,
            identity_sign_pub=vo.identity_sign_pub,
            identity_dh_pub=vo.identity_dh_pub,
            has_active_prekey=vo.has_active_prekey,
            created_at=vo.created_at,
        )
