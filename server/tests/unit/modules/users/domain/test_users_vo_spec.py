from datetime import datetime, timezone
from uuid import uuid4

from app.modules.users.domain.value_objects.list_users_vo import (
    ListUsersQueryVO,
    ListUsersResponseVO,
)
from app.modules.users.domain.value_objects.user_profile_vo import UserProfileVO


def test_users_value_objects():
    """
    ↳ Value objects encapsulan datos inmutables de consulta y respuesta
    """
    uid = uuid4()
    now = datetime.now(timezone.utc)
    user_vo = UserProfileVO(
        id=uid,
        username="alice",
        display_name="Alice",
        identity_sign_pub="sig_pub",
        identity_dh_pub="dh_pub",
        has_active_prekey=False,
        created_at=now,
    )
    assert user_vo.id == uid

    query_vo = ListUsersQueryVO(
        search="ali",
        limit=20,
        offset=0,
        exclude_user_id=uid,
    )
    assert query_vo.search == "ali"
    assert query_vo.limit == 20
    assert query_vo.offset == 0
    assert query_vo.exclude_user_id == uid

    resp_vo = ListUsersResponseVO(
        users=[user_vo],
        total=1,
        limit=20,
        offset=0,
    )
    assert len(resp_vo.users) == 1
    assert resp_vo.total == 1
