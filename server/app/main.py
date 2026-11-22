from fastapi import FastAPI

from app.commons.http.exception_handlers import register_exception_handlers
from app.modules.auth.infrastructure.inbound.http.controllers import auth_controller
from app.modules.health.infrastructure.inbound.http.controllers import health_controller
from app.modules.keys.infrastructure.inbound.http.controllers import keys_controller
from app.modules.users.infrastructure.inbound.http.controllers import users_controller


def create_app() -> FastAPI:
    application = FastAPI(
        title="Ephemeral API",
        version="0.1.0",
    )

    register_exception_handlers(application)

    application.include_router(health_controller.router)
    application.include_router(auth_controller.router)
    application.include_router(keys_controller.router)
    application.include_router(users_controller.router, prefix="/users")

    return application


app = create_app()
