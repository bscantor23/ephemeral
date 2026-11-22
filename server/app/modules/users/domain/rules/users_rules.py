from typing import Optional

from app.modules.users.domain.constants.users_constants import (
    MAX_SEARCH_LENGTH,
    MAX_USERS_LIMIT,
    MIN_USERS_LIMIT,
)
from app.modules.users.domain.errors.users_errors import (
    InvalidPaginationError,
    InvalidSearchQueryError,
)


class UsersRules:
    @staticmethod
    def validate_pagination(limit: int, offset: int) -> None:
        if limit < MIN_USERS_LIMIT or limit > MAX_USERS_LIMIT:
            raise InvalidPaginationError(
                f"Limit must be between {MIN_USERS_LIMIT} and {MAX_USERS_LIMIT}"
            )
        if offset < 0:
            raise InvalidPaginationError("Offset cannot be negative")

    @staticmethod
    def validate_search_query(search: Optional[str]) -> Optional[str]:
        if search is None:
            return None
        cleaned = search.strip()
        if not cleaned:
            return None
        if len(cleaned) > MAX_SEARCH_LENGTH:
            raise InvalidSearchQueryError(
                f"Search query cannot exceed {MAX_SEARCH_LENGTH} characters"
            )
        return cleaned

    @staticmethod
    def normalize_username(username: str) -> str:
        cleaned = username.strip().lstrip("@").lower()
        if not cleaned:
            raise InvalidSearchQueryError("Username cannot be empty")
        return cleaned
