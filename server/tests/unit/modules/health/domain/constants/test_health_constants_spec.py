from app.modules.health.domain.constants.health_constants import (
    DATABASE_OK,
    DATABASE_UNAVAILABLE,
    STATUS_DEGRADED,
    STATUS_OK,
)


def test_health_constants():
    """
    ↳ Constantes: valida valores predeterminados de estado del servicio
    """
    assert STATUS_OK == "ok"
    assert STATUS_DEGRADED == "degraded"
    assert DATABASE_OK == "ok"
    assert DATABASE_UNAVAILABLE == "unavailable"
