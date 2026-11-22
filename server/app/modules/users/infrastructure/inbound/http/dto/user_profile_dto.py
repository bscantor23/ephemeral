from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class UserProfileResponseDTO(BaseModel):
    id: UUID
    username: str
    display_name: str
    identity_sign_pub: str
    identity_dh_pub: str
    has_active_prekey: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ListUsersResponseDTO(BaseModel):
    users: list[UserProfileResponseDTO]
    total: int
    limit: int
    offset: int

    model_config = ConfigDict(from_attributes=True)
