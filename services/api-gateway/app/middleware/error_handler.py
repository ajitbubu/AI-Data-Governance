"""
Enterprise exception handling middleware for FastAPI.

Provides structured JSON error responses with RFC 7807 Problem Details format,
comprehensive error logging, and environment-aware detail levels.
"""
from typing import Callable, Any
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import structlog
import traceback
import uuid
from datetime import datetime, timezone
from ..config import get_settings

settings = get_settings()
logger = structlog.get_logger(__name__)


class DataSafeguardError(Exception):
    """Base exception class for DataSafeguard errors."""

    def __init__(
        self,
        detail: str,
        error_code: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ):
        """
        Initialize DataSafeguardError.

        Args:
            detail: Human-readable error message
            error_code: Machine-readable error code (e.g., "DS-400")
            status_code: HTTP status code
        """
        self.detail = detail
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(detail)


class NotFoundError(DataSafeguardError):
    """Resource not found error."""

    def __init__(self, detail: str, error_code: str = "DS-404"):
        super().__init__(detail, error_code, status.HTTP_404_NOT_FOUND)


class ValidationError(DataSafeguardError):
    """Request validation error."""

    def __init__(self, detail: str, error_code: str = "DS-422"):
        super().__init__(detail, error_code, status.HTTP_422_UNPROCESSABLE_ENTITY)


class AuthorizationError(DataSafeguardError):
    """Authorization/access denied error."""

    def __init__(self, detail: str, error_code: str = "DS-403"):
        super().__init__(detail, error_code, status.HTTP_403_FORBIDDEN)


class AuthenticationError(DataSafeguardError):
    """Authentication/unauthenticated error."""

    def __init__(self, detail: str, error_code: str = "DS-401"):
        super().__init__(detail, error_code, status.HTTP_401_UNAUTHORIZED)


class ConflictError(DataSafeguardError):
    """Resource conflict error."""

    def __init__(self, detail: str, error_code: str = "DS-409"):
        super().__init__(detail, error_code, status.HTTP_409_CONFLICT)


class RateLimitError(DataSafeguardError):
    """Rate limit exceeded error."""

    def __init__(self, detail: str, error_code: str = "DS-429"):
        super().__init__(detail, error_code, status.HTTP_429_TOO_MANY_REQUESTS)


class InternalServerError(DataSafeguardError):
    """Internal server error."""

    def __init__(self, detail: str, error_code: str = "DS-500"):
        super().__init__(detail, error_code, status.HTTP_500_INTERNAL_SERVER_ERROR)


def _get_request_id(request: Request) -> str:
    """Extract request ID from request state or generate new one."""
    if hasattr(request.state, "request_id"):
        return request.state.request_id
    return str(uuid.uuid4())


def _format_error_response(
    status_code: int,
    error_code: str,
    title: str,
    detail: str,
    request_id: str,
    traceback_str: str | None = None,
) -> dict[str, Any]:
    """
    Format error response in RFC 7807 Problem Details format.

    Args:
        status_code: HTTP status code
        error_code: Machine-readable error code
        title: Error title/type
        detail: Human-readable error detail
        request_id: Unique request identifier
        traceback_str: Stack trace (included in debug mode only)

    Returns:
        Structured error response dict
    """
    response = {
        "type": f"urn:datasafeguard:error:{error_code}",
        "title": title,
        "status": status_code,
        "detail": detail,
        "error_code": error_code,
        "request_id": request_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    if settings.DEBUG and traceback_str:
        response["traceback"] = traceback_str

    return response


async def datasafeguard_exception_handler(
    request: Request, exc: DataSafeguardError
) -> JSONResponse:
    """Handle DataSafeguardError exceptions."""
    request_id = _get_request_id(request)

    logger.warning(
        "datasafeguard_error",
        error_code=exc.error_code,
        status_code=exc.status_code,
        detail=exc.detail,
        request_id=request_id,
        path=request.url.path,
        method=request.method,
        client_ip=request.client.host if request.client else "unknown",
    )

    response_body = _format_error_response(
        status_code=exc.status_code,
        error_code=exc.error_code,
        title=exc.error_code,
        detail=exc.detail,
        request_id=request_id,
    )

    return JSONResponse(status_code=exc.status_code, content=response_body)


async def general_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Handle unexpected exceptions."""
    request_id = _get_request_id(request)
    tb_str = traceback.format_exc()

    logger.error(
        "unhandled_exception",
        error_type=type(exc).__name__,
        error_message=str(exc),
        request_id=request_id,
        path=request.url.path,
        method=request.method,
        client_ip=request.client.host if request.client else "unknown",
        exc_info=True,
    )

    response_body = _format_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code="DS-500",
        title="Internal Server Error",
        detail="An unexpected error occurred. Please contact support.",
        request_id=request_id,
        traceback_str=tb_str,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=response_body
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle FastAPI RequestValidationError."""
    request_id = _get_request_id(request)

    # Extract validation errors
    errors = []
    for error in exc.errors():
        errors.append(
            {
                "field": ".".join(str(loc) for loc in error["loc"][1:]),
                "message": error["msg"],
                "type": error["type"],
            }
        )

    logger.warning(
        "validation_error",
        error_code="DS-422",
        request_id=request_id,
        path=request.url.path,
        method=request.method,
        errors=errors,
        client_ip=request.client.host if request.client else "unknown",
    )

    response_body = {
        "type": "urn:datasafeguard:error:DS-422",
        "title": "Validation Error",
        "status": status.HTTP_422_UNPROCESSABLE_ENTITY,
        "detail": "Request validation failed",
        "error_code": "DS-422",
        "request_id": request_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "errors": errors,
    }

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=response_body
    )


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register all exception handlers with FastAPI app.

    Args:
        app: FastAPI application instance
    """
    app.add_exception_handler(DataSafeguardError, datasafeguard_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
