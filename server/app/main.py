from fastapi import FastAPI

from app.modules.health.infrastructure.inbound.controllers import health_controller


def create_app() -> FastAPI:
    application = FastAPI(
        title="Ephemeral API",
        version="0.1.0",
    )

    application.include_router(health_controller.router)

    return application


app = create_app()
