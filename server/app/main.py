import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.commons.config.settings import get_settings
from app.commons.http.exception_handlers import register_exception_handlers
from app.modules.auth.infrastructure.inbound.http.controllers import auth_controller
from app.modules.health.infrastructure.inbound.http.controllers import health_controller
from app.modules.keys.infrastructure.inbound.http.controllers import keys_controller
from app.modules.messages.infrastructure.inbound.http.controllers import (
    messages_controller,
)
from app.modules.messages.infrastructure.inbound.websocket import (
    websocket_controller,
)
from app.modules.messages.infrastructure.outbound.scheduler.purge_worker import (
    run_periodic_purge,
)
from app.modules.users.infrastructure.inbound.http.controllers import users_controller


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    purge_task = None
    if settings.ENABLE_PURGE_WORKER:
        purge_task = asyncio.create_task(run_periodic_purge())
    yield
    if purge_task:
        purge_task.cancel()
        try:
            await purge_task
        except asyncio.CancelledError:
            pass


def create_app() -> FastAPI:
    application = FastAPI(
        title="Ephemeral API",
        version="0.1.0",
        lifespan=lifespan,
    )

    register_exception_handlers(application)

    application.include_router(health_controller.router)
    application.include_router(auth_controller.router)
    application.include_router(keys_controller.router)
    application.include_router(users_controller.router, prefix="/users")
    application.include_router(messages_controller.router, prefix="/messages")
    application.include_router(websocket_controller.ws_router)

    return application


app = create_app()
