from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
import pytest

from app.modules.auth.domain.value_objects.auth_token_vo import AuthTokenVO


def test_auth_token_vo():
    """
    ↳ AuthTokenVO: almacena tupla criptografica de token de forma inmutable
    """
    now = datetime.now(timezone.utc)
    vo = AuthTokenVO(
        raw_token="raw_xyz",
        token_hash="sha256_hash",
        expires_at=now,
    )
    assert vo.raw_token == "raw_xyz"
    assert vo.token_hash == "sha256_hash"
    assert vo.expires_at == now

    with pytest.raises(FrozenInstanceError):
        vo.raw_token = "modified"
