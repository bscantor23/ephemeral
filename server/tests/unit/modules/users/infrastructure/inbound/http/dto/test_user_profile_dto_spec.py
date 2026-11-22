from datetime import datetime, timezone
from uuid import uuid4

from app.modules.users.infrastructure.inbound.http.dto.user_profile_dto import (
    ListUsersResponseDTO,
    UserProfileResponseDTO,
)


def test_user_profile_dto_serialization():
    """
    ↳ DTO serializa correctamente datos de perfil y lista
    """
    uid = uuid4()
    now = datetime.now(timezone.utc)
    user_dto = UserProfileResponseDTO(
        id=uid,
        username="alice",
        display_name="Alice",
        identity_sign_pub="sig_pub",
        identity_dh_pub="dh_pub",
        has_active_prekey=True,
        created_at=now,
    )
    assert user_dto.id == uid
    assert user_dto.has_active_prekey is True

    list_dto = ListUsersResponseDTO(
        users=[user_dto],
        total=1,
        limit=50,
        offset=0,
    )
    assert len(list_dto.users) == 1
    assert list_dto.total == 1
