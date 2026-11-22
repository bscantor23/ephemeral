from app.modules.health.application.ports.check_health_port import (
    CheckHealthPort,
)
from app.modules.health.infrastructure.inbound.http.dependencies import (
    get_check_health_use_case,
)


def test_health_dependencies_factory():
    """
    ↳ Dependencias: get_check_health_use_case fabrica instancia de CheckHealthPort
    """
    uc = get_check_health_use_case()
    assert CheckHealthPort in type(uc).__mro__
