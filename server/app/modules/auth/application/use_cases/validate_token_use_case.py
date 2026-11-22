from app.modules.auth.application.ports.validate_token_port import (
    ValidateTokenPort,
)
from app.modules.auth.domain.errors.auth_errors import (
    InvalidCredentialsError,
    UserNotFoundError,
)
from app.modules.auth.domain.ports.session_repository_port import (
    SessionRepositoryPort,
)
from app.modules.auth.domain.ports.token_service_port import TokenServicePort
from app.modules.auth.domain.ports.user_repository_port import (
    UserRepositoryPort,
)
from app.modules.auth.domain.rules.auth_rules import AuthRules
from app.modules.auth.domain.value_objects.user_response_vo import UserResponseVO


class ValidateTokenUseCase(ValidateTokenPort):
    def __init__(
        self,
        session_repo: SessionRepositoryPort,
        user_repo: UserRepositoryPort,
        token_service: TokenServicePort,
    ) -> None:
        self._session_repo = session_repo
        self._user_repo = user_repo
        self._token_service = token_service

    def execute(self, raw_token: str) -> UserResponseVO:
        token_hash = self._token_service.hash_token(raw_token)
        session = self._session_repo.get_by_token_hash(token_hash)
        if session is None:
            raise InvalidCredentialsError("Invalid or missing session token")

        AuthRules.validate_session_active(session)

        user = self._user_repo.get_by_id(session.user_id)
        if user is None:
            raise UserNotFoundError("User associated with session does not exist")

        return UserResponseVO.from_entity(user)
