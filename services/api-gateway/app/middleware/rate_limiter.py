"""
Redis-backed sliding window rate limiter middleware.

Uses pure ASGI middleware (not BaseHTTPMiddleware) to avoid
Starlette's known request body streaming deadlock on POST requests.
"""
import time
import json
from typing import Set
from starlette.types import ASGIApp, Receive, Scope, Send
import redis.asyncio as redis
import structlog
from ..config import get_settings
from .request_context import get_request_id

settings = get_settings()
logger = structlog.get_logger(__name__)

# Endpoints that bypass rate limiting
RATE_LIMIT_BYPASS_PATHS: Set[str] = {
    "/health",
    "/health/live",
    "/health/ready",
    "/metrics",
    "/docs",
    "/redoc",
    "/openapi.json",
}


class RateLimiter:
    """Redis-backed sliding window rate limiter."""

    def __init__(self, redis_url: str):
        """
        Initialize rate limiter.

        Args:
            redis_url: Redis connection URL
        """
        self.redis_url = redis_url
        self.redis_client: redis.Redis | None = None
        self.redis_available = False

    async def connect(self) -> None:
        """Establish Redis connection with timeout."""
        try:
            self.redis_client = await redis.from_url(
                self.redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=3,
            )
            # Test connection
            await self.redis_client.ping()
            self.redis_available = True
            logger.info("redis_connection_established")
        except Exception as e:
            logger.warning("redis_connection_failed", error=str(e))
            self.redis_available = False

    async def disconnect(self) -> None:
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()
            self.redis_available = False

    async def is_allowed(
        self, client_ip: str, limit: int, window_seconds: int = 60
    ) -> tuple[bool, dict]:
        """
        Check if client is within rate limit using sliding window.

        Args:
            client_ip: Client IP address
            limit: Maximum requests allowed in window
            window_seconds: Time window in seconds

        Returns:
            Tuple of (allowed: bool, info: dict with rate limit details)
        """
        # If Redis unavailable, allow request but log warning
        if not self.redis_available:
            logger.warning(
                "rate_limit_skipped_redis_unavailable", client_ip=client_ip
            )
            return True, {
                "limit": limit,
                "remaining": limit,
                "reset": int(time.time()) + window_seconds,
            }

        try:
            current_time = time.time()
            window_start = current_time - window_seconds
            key = f"rate_limit:{client_ip}"

            # Remove old entries outside window
            await self.redis_client.zremrangebyscore(key, 0, window_start)

            # Count requests in window
            current_count = await self.redis_client.zcard(key)

            # Create info dict
            reset_time = int(current_time) + window_seconds
            info = {
                "limit": limit,
                "remaining": max(0, limit - current_count),
                "reset": reset_time,
            }

            # If at limit, reject
            if current_count >= limit:
                return False, info

            # Add current request with timestamp as score
            await self.redis_client.zadd(key, {str(current_time): current_time})
            # Set expiration
            await self.redis_client.expire(key, window_seconds + 1)

            return True, info

        except Exception as e:
            logger.warning("rate_limit_check_failed", error=str(e), client_ip=client_ip)
            # Graceful degradation: allow request if check fails
            return True, {
                "limit": limit,
                "remaining": limit,
                "reset": int(time.time()) + window_seconds,
            }


# Global rate limiter instance
_rate_limiter: RateLimiter | None = None


def get_rate_limiter() -> RateLimiter:
    """Get or create global rate limiter instance."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter(settings.REDIS_URL)
    return _rate_limiter


async def init_rate_limiter() -> None:
    """Initialize rate limiter connection."""
    limiter = get_rate_limiter()
    await limiter.connect()


async def shutdown_rate_limiter() -> None:
    """Shutdown rate limiter connection."""
    limiter = get_rate_limiter()
    await limiter.disconnect()


def _should_rate_limit(path: str) -> bool:
    """Check if path should be rate limited."""
    for bypass_path in RATE_LIMIT_BYPASS_PATHS:
        if path.startswith(bypass_path):
            return False
    return True


def _is_write_endpoint(method: str) -> bool:
    """Determine if endpoint is write operation."""
    return method.upper() in {"POST", "PUT", "PATCH", "DELETE"}


class RateLimitMiddleware:
    """
    Pure ASGI rate limiting middleware using Redis sliding window.

    Does NOT use BaseHTTPMiddleware to avoid request body streaming deadlock.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")
        method = scope.get("method", "")

        # Skip rate limiting for health checks, OPTIONS (CORS preflight), and docs
        if not _should_rate_limit(path) or method == "OPTIONS":
            await self.app(scope, receive, send)
            return

        # Get client IP
        client = scope.get("client")
        client_ip = client[0] if client else "unknown"

        # Determine rate limit based on endpoint type
        is_write = _is_write_endpoint(method)
        limit = (
            settings.RATE_LIMIT_WRITE_PER_MINUTE
            if is_write
            else settings.RATE_LIMIT_PER_MINUTE
        )

        # Check rate limit
        limiter = get_rate_limiter()
        allowed, rate_info = await limiter.is_allowed(client_ip, limit, 60)

        if not allowed:
            request_id = get_request_id()
            logger.warning(
                "rate_limit_exceeded",
                client_ip=client_ip,
                path=path,
                method=method,
                request_id=request_id,
            )

            error_body = json.dumps({
                "type": "urn:datasafeguard:error:DS-429",
                "title": "Too Many Requests",
                "status": 429,
                "detail": "Rate limit exceeded. Please retry after some time.",
                "error_code": "DS-429",
                "request_id": request_id,
            }).encode("utf-8")

            retry_after = str(max(1, rate_info["reset"] - int(time.time())))
            headers = [
                (b"content-type", b"application/json"),
                (b"retry-after", retry_after.encode()),
                (b"x-ratelimit-limit", str(rate_info["limit"]).encode()),
                (b"x-ratelimit-remaining", str(rate_info["remaining"]).encode()),
                (b"x-ratelimit-reset", str(rate_info["reset"]).encode()),
            ]

            await send({"type": "http.response.start", "status": 429, "headers": headers})
            await send({"type": "http.response.body", "body": error_body})
            return

        # Add rate limit headers to the response
        async def send_with_rate_headers(message):
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                headers.append((b"x-ratelimit-limit", str(rate_info["limit"]).encode()))
                headers.append((b"x-ratelimit-remaining", str(rate_info["remaining"]).encode()))
                headers.append((b"x-ratelimit-reset", str(rate_info["reset"]).encode()))
                message["headers"] = headers
            await send(message)

        await self.app(scope, receive, send_with_rate_headers)
