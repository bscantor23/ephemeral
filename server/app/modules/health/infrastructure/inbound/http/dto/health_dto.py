from pydantic import BaseModel, ConfigDict


class HealthResponseDto(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)

    status: str
    database: str
