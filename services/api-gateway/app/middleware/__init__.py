"""
Middleware components for enterprise-grade hardening.

Includes error handling, request context tracking, rate limiting,
structured logging, and JWT authentication with RBAC.
"""

# Error handling
from .error_handler import (
    DataSafeguardError,
    NotFoundError,
    ValidationError,
    AuthorizationError,
    AuthenticationError,
    ConflictError,
    RateLimitError,
    InternalServerError,
    register_exception_handlers,
)

# Request context
from .request_context import (
    RequestContextMiddleware,
    get_request_id,
    set_request_id,
    get_user_id,
    set_user_id,
    get_user_email,
    set_user_email,
)

# Rate limiting
from .rate_limiter import (
    RateLimitMiddleware,
    init_rate_limiter,
    shutdown_rate_limiter,
    get_rate_limiter,
)

# Logging
from .logging_middleware import (
    LoggingMiddleware,
    setup_logging,
    get_logger,
)

# Authentication and RBAC
from .auth import (
    CurrentUser,
    get_current_user,
    require_role,
    require_any_role,
    require_all_roles,
    create_access_token,
    VALID_ROLES,
)

__all__ = [
    # Error handling
    "DataSafeguardError",
    "NotFoundError",
    "ValidationError",
    "AuthorizationError",
    "AuthenticationError",
    "ConflictError",
    "RateLimitError",
    "InternalServerError",
    "register_exception_handlers",
    # Request context
    "RequestContextMiddleware",
    "get_request_id",
    "set_request_id",
    "get_user_id",
    "set_user_id",
    "get_user_email",
    "set_user_email",
    # Rate limiting
    "RateLimitMiddleware",
    "init_rate_limiter",
    "shutdown_rate_limiter",
    "get_rate_limiter",
    # Logging
    "LoggingMiddleware",
    "setup_logging",
    "get_logger",
    # Authentication and RBAC
    "CurrentUser",
    "get_current_user",
    "require_role",
    "require_any_role",
    "require_all_roles",
    "create_access_token",
    "VALID_ROLES",
]
