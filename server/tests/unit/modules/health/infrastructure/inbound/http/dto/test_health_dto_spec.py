from app.modules.health.domain.value_objects.health_status_vo import (
    HealthStatusVO,
)
from app.modules.health.infrastructure.inbound.http.dto.health_dto import (
    HealthResponseDto,
)


def test_health_response_dto_from_attributes():
    """
    ↳ DTO: HealthResponseDto serializa desde HealthStatusVO via from_attributes
    """
    vo = HealthStatusVO(status="ok", database="ok", is_healthy=True)
    dto = HealthResponseDto.model_validate(vo)
    assert dto.status == "ok"
    assert dto.database == "ok"
