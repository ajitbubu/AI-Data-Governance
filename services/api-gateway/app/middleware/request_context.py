"""
Request context middleware for distributed tracing.

Uses pure ASGI middleware (not BaseHTTPMiddleware) to avoid
Starlette's known request body streaming issues.
"""
import uuid
import time
from contextvars import ContextVar
from starlette.types import ASGIApp, Receive, Scope, Send

# Context variables accessible throughout request lifecycle
_request_id_ctx: ContextVar[str] = ContextVar("request_id", default="")
_user_id_ctx: ContextVar[str | None] = ContextVar("user_id", default=None)
_user_email_ctx: ContextVar[str | None] = ContextVar("user_email", default=None)


def get_request_id() -> str:
    return _request_id_ctx.get()


def set_request_id(request_id: str) -> None:
    _request_id_ctx.set(request_id)


def get_user_id() -> str | None:
    return _user_id_ctx.get()


def set_user_id(user_id: str | None) -> None:
    _user_id_ctx.set(user_id)


def get_user_email() -> str | None:
    return _user_email_ctx.get()


def set_user_email(user_email: str | None) -> None:
    _user_email_ctx.set(user_email)


class RequestContextMiddleware:
    """
    Pure ASGI middleware that generates request IDs and tracks timing.

    Does NOT use BaseHTTPMiddleware to avoid request body streaming issues.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        # Generate or extract request ID from headers
        request_id = str(uuid.uuid4())
        for header_name, header_value in scope.get("headers", []):
            if header_name == b"x-request-id":
                request_id = header_value.decode("utf-8")
                break

        set_request_id(request_id)

        # Store in scope state for access in handlers
        if "state" not in scope:
            scope["state"] = {}
        scope["state"]["request_id"] = request_id

        start_time = time.time()

        async def send_with_headers(message):
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                process_time_ms = int((time.time() - start_time) * 1000)
                headers.append((b"x-request-id", request_id.encode()))
                headers.append((b"x-process-time", str(process_time_ms).encode()))
                message["headers"] = headers
            await send(message)

        await self.app(scope, receive, send_with_headers)
