import pytest

from app.modules.auth.domain.ports.password_hasher_port import (
    PasswordHasherPort,
)
from app.modules.auth.infrastructure.outbound.adapters.pynacl_argon2_adapter import (
    PyNaClArgon2Adapter,
)


@pytest.mark.anyio
async def test_argon2_hash_and_verify():
    """
    ↳ Adaptador Argon2id: genera hash valido y verifica coincidencia
    """
    adapter = PyNaClArgon2Adapter(max_concurrency=2)
    password = "SuperSecurePassword123!"

    hashed = await adapter.hash_password(password)
    assert hashed.startswith("$argon2id$")

    assert await adapter.verify_password(hashed, password) is True
    assert await adapter.verify_password(hashed, "wrong_password") is False


@pytest.mark.anyio
async def test_argon2_verify_invalid_hash_returns_false():
    """
    ↳ Adaptador Argon2id: hash corrupto o invalido retorna False sin explotar
    """
    adapter = PyNaClArgon2Adapter(max_concurrency=1)
    is_valid = await adapter.verify_password("invalid_hash_format", "password")
    assert is_valid is False


def test_argon2_adapter_port_mro():
    """
    ↳ Adaptador Argon2id: PyNaClArgon2Adapter implementa PasswordHasherPort en su MRO
    """
    assert PasswordHasherPort in PyNaClArgon2Adapter.__mro__
