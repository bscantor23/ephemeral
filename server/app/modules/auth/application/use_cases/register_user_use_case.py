from app.modules.auth.application.ports.register_user_port import RegisterUserPort
from app.modules.auth.domain.entities.user_entity import UserEntity
from app.modules.auth.domain.errors.auth_errors import UserAlreadyExistsError
from app.modules.auth.domain.ports.password_hasher_port import (
    PasswordHasherPort,
)
from app.modules.auth.domain.ports.user_repository_port import (
    UserRepositoryPort,
)
from app.modules.auth.domain.rules.auth_rules import AuthRules
from app.modules.auth.domain.value_objects.register_user_request_vo import (
    RegisterUserRequestVO,
)
from app.modules.auth.domain.value_objects.user_response_vo import UserResponseVO


class RegisterUserUseCase(RegisterUserPort):
    def __init__(self, user_repo: UserRepositoryPort, hasher: PasswordHasherPort) -> None:
        self._user_repo = user_repo
        self._hasher = hasher

    async def execute(self, request: RegisterUserRequestVO) -> UserResponseVO:
        normalized_username = AuthRules.normalize_username(request.username)
        existing_user = self._user_repo.get_by_username(normalized_username)
        if existing_user is not None:
            raise UserAlreadyExistsError("Username is already taken")

        password_hash = await self._hasher.hash_password(request.password)

        user = UserEntity.create(
            username=normalized_username,
            display_name=request.display_name,
            password_hash=password_hash,
            identity_sign_pub=request.identity_sign_pub,
            identity_dh_pub=request.identity_dh_pub,
            identity_dh_sig=request.identity_dh_sig,
        )
        saved_user = self._user_repo.save(user)
        return UserResponseVO.from_entity(saved_user)
