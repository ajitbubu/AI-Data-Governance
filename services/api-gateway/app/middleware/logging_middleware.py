"""
Structured JSON logging middleware for FastAPI.

Uses pure ASGI middleware (not BaseHTTPMiddleware) to avoid
Starlette's known request body streaming deadlock.
"""
import time
import sys
import logging
from starlette.types import ASGIApp, Receive, Scope, Send
import structlog
from .request_context import get_request_id, get_user_id, get_user_email


def setup_logging(debug: bool = False) -> None:
    """
    Configure structlog for production or development.

    In production: JSON output for log aggregation
    In development: colored console output for readability
    """
    shared_processors = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.contextvars.merge_contextvars,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    if debug:
        structlog.configure(
            processors=shared_processors
            + [structlog.dev.ConsoleRenderer(colors=True)],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )
        logging.basicConfig(level=logging.DEBUG, format="%(message)s")
    else:
        structlog.configure(
            processors=shared_processors
            + [structlog.processors.JSONRenderer()],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )
        logging.basicConfig(level=logging.INFO, format="%(message)s")


def get_logger(name: str | None = None) -> structlog.BoundLogger:
    if name is None:
        name = __name__
    return structlog.get_logger(name)


class LoggingMiddleware:
    """
    Pure ASGI middleware that logs all HTTP requests with structured data.

    Does NOT use BaseHTTPMiddleware to avoid request body streaming deadlock.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        logger = get_logger(__name__)
        request_id = get_request_id()
        user_id = get_user_id()

        path = scope.get("path", "")
        method = scope.get("method", "")
        client = scope.get("client")
        client_ip = client[0] if client else "unknown"

        bound_logger = logger.bind(
            request_id=request_id,
            user_id=user_id,
            client_ip=client_ip,
        )

        bound_logger.info(
            "http_request_received",
            method=method,
            path=path,
        )

        start_time = time.time()
        status_code = 0

        async def send_wrapper(message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message.get("status", 0)
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as exc:
            duration_ms = int((time.time() - start_time) * 1000)
            bound_logger.exception(
                "http_request_error",
                method=method,
                path=path,
                duration_ms=duration_ms,
                error_type=type(exc).__name__,
            )
            raise

        duration_ms = int((time.time() - start_time) * 1000)

        if status_code >= 500:
            log_fn = bound_logger.error
        elif status_code >= 400:
            log_fn = bound_logger.warning
        else:
            log_fn = bound_logger.info

        log_fn(
            "http_response_sent",
            method=method,
            path=path,
            status_code=status_code,
            duration_ms=duration_ms,
        )
