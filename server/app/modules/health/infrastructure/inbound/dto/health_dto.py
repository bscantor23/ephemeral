from pydantic import BaseModel, ConfigDict


class HealthResponseDto(BaseModel):
    model_config = ConfigDict(frozen=True)

    status: str
    database: str
