import pytest

from app.modules.users.domain.errors.users_errors import (
    InvalidPaginationError,
    InvalidSearchQueryError,
)
from app.modules.users.domain.rules.users_rules import UsersRules


def test_validate_pagination_success():
    """
    ↳ Validacion de paginacion exitosa dentro de limites
    """
    UsersRules.validate_pagination(limit=10, offset=0)
    UsersRules.validate_pagination(limit=50, offset=100)
    UsersRules.validate_pagination(limit=100, offset=0)


def test_validate_pagination_limit_out_of_bounds():
    """
    ↳ Error cuando limit es menor a 1 o mayor a 100
    """
    with pytest.raises(InvalidPaginationError, match="Limit must be between 1 and 100"):
        UsersRules.validate_pagination(limit=0, offset=0)

    with pytest.raises(InvalidPaginationError, match="Limit must be between 1 and 100"):
        UsersRules.validate_pagination(limit=101, offset=0)


def test_validate_pagination_negative_offset():
    """
    ↳ Error cuando offset es negativo
    """
    with pytest.raises(InvalidPaginationError, match="Offset cannot be negative"):
        UsersRules.validate_pagination(limit=10, offset=-1)


def test_validate_search_query():
    """
    ↳ Validacion y sanitizado de query de busqueda
    """
    assert UsersRules.validate_search_query(None) is None
    assert UsersRules.validate_search_query("   ") is None
    assert UsersRules.validate_search_query("  bob  ") == "bob"

    long_str = "a" * 65
    with pytest.raises(InvalidSearchQueryError, match="Search query cannot exceed 64 characters"):
        UsersRules.validate_search_query(long_str)


def test_normalize_username():
    """
    ↳ Normalizacion de username eliminando arrobas y espacios
    """
    assert UsersRules.normalize_username("@Alice") == "alice"
    assert UsersRules.normalize_username("  Bob  ") == "bob"
    assert UsersRules.normalize_username("@@carol") == "carol"

    with pytest.raises(InvalidSearchQueryError, match="Username cannot be empty"):
        UsersRules.normalize_username("   @   ")
