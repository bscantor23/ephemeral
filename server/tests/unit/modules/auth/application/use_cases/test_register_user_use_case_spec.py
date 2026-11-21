from typing import Optional
from uuid import UUID
import pytest

from app.modules.auth.application.ports.register_user_port import RegisterUserPort
from app.modules.auth.application.use_cases.register_user_use_case import (
    RegisterUserUseCase,
)
from app.modules.auth.domain.entities.user_entity import UserEntity
from app.modules.auth.domain.errors.auth_errors import UserAlreadyExistsError
from app.modules.auth.domain.value_objects.register_user_request_vo import (
    RegisterUserRequestVO,
)
from app.modules.auth.domain.value_objects.user_response_vo import UserResponseVO


class FakeUserRepository:
    def __init__(self) -> None:
        self.users: dict[str, UserEntity] = {}

    def save(self, user: UserEntity) -> UserEntity:
        self.users[user.username] = user
        return user

    def get_by_id(self, user_id: UUID) -> Optional[UserEntity]:
        for u in self.users.values():
            if u.id == user_id:
                return u
        return None

    def get_by_username(self, username: str) -> Optional[UserEntity]:
        return self.users.get(username.lower())


class FakeHasher:
    async def hash_password(self, password: str) -> str:
        return f"hashed_{password}"

    async def verify_password(self, password_hash: str, password: str) -> bool:
        return password_hash == f"hashed_{password}"


@pytest.mark.anyio
async def test_register_user_success():
    """
    ↳ Caso de uso: registro exitoso persiste y retorna nuevo usuario
    """
    repo = FakeUserRepository()
    hasher = FakeHasher()
    use_case = RegisterUserUseCase(user_repo=repo, hasher=hasher)

    reg = RegisterUserRequestVO(
        username="Alice",
        display_name="Alice Smith",
        password="secretpassword",
        identity_sign_pub="sign_pub_key",
        identity_dh_pub="dh_pub_key",
        identity_dh_sig="dh_sig_bytes",
    )
    user = await use_case.execute(reg)

    assert isinstance(user, UserResponseVO)
    assert user.username == "alice"
    assert user.display_name == "Alice Smith"
    saved = repo.get_by_username("alice")
    assert saved is not None
    assert saved.password_hash == "hashed_secretpassword"


@pytest.mark.anyio
async def test_register_user_fallback_display_name():
    """
    ↳ Caso de uso: display_name vacio utiliza username como display_name por defecto
    """
    repo = FakeUserRepository()
    hasher = FakeHasher()
    use_case = RegisterUserUseCase(user_repo=repo, hasher=hasher)

    reg = RegisterUserRequestVO(
        username="alice",
        display_name="   ",
        password="secretpassword",
        identity_sign_pub="k1",
        identity_dh_pub="k2",
        identity_dh_sig="s1",
    )
    user = await use_case.execute(reg)
    assert user.display_name == "alice"


@pytest.mark.anyio
async def test_register_duplicate_username_fails():
    """
    ↳ Caso de uso: username duplicado lanza UserAlreadyExistsError
    """
    repo = FakeUserRepository()
    hasher = FakeHasher()
    use_case = RegisterUserUseCase(user_repo=repo, hasher=hasher)

    reg = RegisterUserRequestVO(
        username="alice",
        display_name="Alice",
        password="secretpassword",
        identity_sign_pub="k1",
        identity_dh_pub="k2",
        identity_dh_sig="s1",
    )
    await use_case.execute(reg)

    with pytest.raises(UserAlreadyExistsError):
        await use_case.execute(reg)


def test_register_user_use_case_port_mro():
    """
    ↳ Caso de uso: RegisterUserUseCase implementa RegisterUserPort en su MRO
    """
    assert RegisterUserPort in RegisterUserUseCase.__mro__
