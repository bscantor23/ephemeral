from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.commons.errors.base_errors import ApplicationError, DomainError
from app.modules.auth.domain.errors.auth_errors import (
    InvalidCredentialsError,
    RateLimitExceededError,
    SessionExpiredError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.modules.health.domain.errors.health_errors import ServiceUnavailableError
from app.modules.keys.domain.errors.keys_errors import (
    NoActivePrekeyError,
    PrekeyExpiredError,
    TargetUserNotFoundError,
)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ServiceUnavailableError)
    async def service_unavailable_handler(
        request: Request, exc: ServiceUnavailableError
    ) -> JSONResponse:
        content = (
            {"detail": exc.detail} if exc.detail is not None else {"detail": str(exc)}
        )
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content=content
        )

    @app.exception_handler(UserAlreadyExistsError)
    async def user_exists_handler(
        request: Request, exc: UserAlreadyExistsError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT, content={"detail": str(exc)}
        )

    @app.exception_handler(RateLimitExceededError)
    async def rate_limit_handler(
        request: Request, exc: RateLimitExceededError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": str(exc)},
        )

    @app.exception_handler(TargetUserNotFoundError)
    @app.exception_handler(NoActivePrekeyError)
    @app.exception_handler(PrekeyExpiredError)
    async def not_found_handler(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)},
        )

    @app.exception_handler(InvalidCredentialsError)
    @app.exception_handler(SessionExpiredError)
    @app.exception_handler(UserNotFoundError)
    async def unauthorized_handler(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": str(exc)},
            headers={"WWW-Authenticate": "Bearer"},
        )

    @app.exception_handler(DomainError)
    async def domain_error_handler(
        request: Request, exc: DomainError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": str(exc)},
        )

    @app.exception_handler(ApplicationError)
    async def application_error_handler(
        request: Request, exc: ApplicationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exc)}
        )
