from fastapi import APIRouter, Depends, status

from app.modules.health.application.ports.check_health_port import CheckHealthPort
from app.modules.health.domain.value_objects.health_status_vo import HealthStatusVO
from app.modules.health.infrastructure.inbound.http.dependencies import (
    get_check_health_use_case,
)
from app.modules.health.infrastructure.inbound.http.dto.health_dto import (
    HealthResponseDto,
)

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponseDto, status_code=status.HTTP_200_OK)
def get_health(
    use_case: CheckHealthPort = Depends(get_check_health_use_case),
) -> HealthStatusVO:
    return use_case.execute()
