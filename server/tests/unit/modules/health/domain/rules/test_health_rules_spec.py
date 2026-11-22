from app.modules.health.domain.constants import health_constants
from app.modules.health.domain.rules.health_rules import HealthRules


def test_health_rules_evaluate_connected():
    """
    ↳ Reglas: base de datos conectada retorna estado ok y saludable
    """
    res = HealthRules.evaluate(is_database_connected=True)
    assert res.status == health_constants.STATUS_OK
    assert res.database == health_constants.DATABASE_OK
    assert res.is_healthy is True


def test_health_rules_evaluate_disconnected():
    """
    ↳ Reglas: base de datos desconectada retorna estado degradado
    """
    res = HealthRules.evaluate(is_database_connected=False)
    assert res.status == health_constants.STATUS_DEGRADED
    assert res.database == health_constants.DATABASE_UNAVAILABLE
    assert res.is_healthy is False
