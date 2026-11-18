from fastapi import APIRouter, Depends, HTTPException, status

from app.modules.health.application.ports.check_health_port import CheckHealthPort
from app.modules.health.application.use_cases.check_health_use_case import CheckHealthUseCase
from app.modules.health.infrastructure.inbound.dto.health_dto import HealthResponseDto
from app.modules.health.infrastructure.outbound.persistence.database_health_adapter import DatabaseHealthAdapter

router = APIRouter(tags=["Health"])


def get_check_health_use_case() -> CheckHealthPort:
    adapter = DatabaseHealthAdapter()
    return CheckHealthUseCase(db_health_port=adapter)


@router.get("/health", response_model=HealthResponseDto, status_code=status.HTTP_200_OK)
def get_health(use_case: CheckHealthPort = Depends(get_check_health_use_case)) -> HealthResponseDto:
    health_status = use_case.execute()
    if not health_status.is_healthy:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=HealthResponseDto(
                status=health_status.status,
                database=health_status.database,
            ).model_dump(),
        )
    return HealthResponseDto(
        status=health_status.status,
        database=health_status.database,
    )
