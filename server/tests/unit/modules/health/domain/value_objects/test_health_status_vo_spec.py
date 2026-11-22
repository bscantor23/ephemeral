from dataclasses import FrozenInstanceError
import pytest

from app.modules.health.domain.value_objects.health_status_vo import (
    HealthStatusVO,
)


def test_health_status_vo_attributes():
    """
    ↳ HealthStatusVO: almacena estado, conectividad y bandera is_healthy de forma inmutable
    """
    vo = HealthStatusVO(status="ok", database="ok", is_healthy=True)
    assert vo.status == "ok"
    assert vo.database == "ok"
    assert vo.is_healthy is True

    with pytest.raises(FrozenInstanceError):
        vo.status = "degraded"
