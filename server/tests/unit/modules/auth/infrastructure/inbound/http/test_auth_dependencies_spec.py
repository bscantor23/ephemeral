from app.modules.auth.application.ports.login_user_port import LoginUserPort
from app.modules.auth.application.ports.logout_user_port import LogoutUserPort
from app.modules.auth.application.ports.register_user_port import RegisterUserPort
from app.modules.auth.infrastructure.inbound.http.dependencies import (
    get_login_user_use_case,
    get_logout_user_use_case,
    get_register_user_use_case,
    hasher_singleton,
    rate_limiter_singleton,
)


def test_auth_dependencies_factories():
    """
    ↳ Dependencias: fabricas instancian casos de uso implementando sus puertos
    """
    reg_uc = get_register_user_use_case()
    assert RegisterUserPort in type(reg_uc).__mro__

    login_uc = get_login_user_use_case()
    assert LoginUserPort in type(login_uc).__mro__

    logout_uc = get_logout_user_use_case()
    assert LogoutUserPort in type(logout_uc).__mro__

    assert rate_limiter_singleton is not None
    assert hasher_singleton is not None
