from app.modules.auth.domain.ports.token_service_port import TokenServicePort
from app.modules.auth.domain.value_objects.auth_token_vo import AuthTokenVO
from app.modules.auth.infrastructure.outbound.adapters.token_service_adapter import (
    TokenServiceAdapter,
)


def test_token_service_generate_and_hash():
    """
    ↳ Adaptador Tokens: genera token raw, calcula SHA-256 y fecha expiracion
    """
    service = TokenServiceAdapter()
    token = service.generate_token(ttl_minutes=15)

    assert isinstance(token, AuthTokenVO)
    assert len(token.raw_token) > 20
    assert len(token.token_hash) == 64
    assert token.token_hash == service.hash_token(token.raw_token)
    assert token.expires_at is not None


def test_token_service_port_mro():
    """
    ↳ Adaptador Tokens: TokenServiceAdapter implementa TokenServicePort en su MRO
    """
    assert TokenServicePort in TokenServiceAdapter.__mro__
