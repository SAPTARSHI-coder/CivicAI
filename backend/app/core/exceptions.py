"""Domain exceptions and centralized exception handlers.

Application code raises typed ``AppException`` subclasses; the registered
handlers translate them into consistent JSON error envelopes. This keeps
endpoint code free of try/except boilerplate.
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import get_logger

logger = get_logger(__name__)


class AppException(Exception):
    """Base class for all application-level errors."""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code: str = "internal_error"
    message: str = "An unexpected error occurred."

    def __init__(self, message: str | None = None, *, details: Any = None) -> None:
        self.message = message or self.message
        self.details = details
        super().__init__(self.message)


class NotFoundError(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    error_code = "not_found"
    message = "Resource not found."


class ConflictError(AppException):
    status_code = status.HTTP_409_CONFLICT
    error_code = "conflict"
    message = "Resource conflict."


class UnauthorizedError(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = "unauthorized"
    message = "Authentication required."


class ForbiddenError(AppException):
    status_code = status.HTTP_403_FORBIDDEN
    error_code = "forbidden"
    message = "You do not have permission to perform this action."


class ValidationAppError(AppException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    error_code = "validation_error"
    message = "Validation failed."


def _error_body(error_code: str, message: str, details: Any = None) -> dict[str, Any]:
    body: dict[str, Any] = {"error": {"code": error_code, "message": message}}
    if details is not None:
        body["error"]["details"] = details
    return body


def register_exception_handlers(app: FastAPI) -> None:
    """Attach all exception handlers to the application."""

    @app.exception_handler(AppException)
    async def _app_exception_handler(_request: Request, exc: AppException) -> JSONResponse:
        if exc.status_code >= 500:
            logger.error("app.exception", error_code=exc.error_code, message=exc.message)
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_body(exc.error_code, exc.message, exc.details),
        )

    @app.exception_handler(RequestValidationError)
    async def _validation_handler(_request: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=_error_body("validation_error", "Validation failed.", exc.errors()),
        )

    @app.exception_handler(StarletteHTTPException)
    async def _http_exception_handler(_request: Request, exc: StarletteHTTPException) -> JSONResponse:
        if exc.status_code == 500:
            logger.exception("http.500_error", error=str(exc))
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_body("http_error", str(exc.detail)),
        )

    @app.exception_handler(Exception)
    async def _unhandled_handler(_request: Request, exc: Exception) -> JSONResponse:
        logger.exception("unhandled.exception", error=str(exc))
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_error_body("internal_error", "An unexpected error occurred."),
        )
