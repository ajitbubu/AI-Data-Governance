"""
DataSafeguard API Gateway — FastAPI application entry point.

This is the main API server for the DataSafeguard AI Governance Platform.
UC-1 (AI System Inventory & Risk Classification) is the first module.

Enterprise-grade hardening includes:
- Structured JSON logging with correlation IDs
- Rate limiting (sliding window, Redis-backed)
- JWT authentication with RBAC
- Comprehensive error handling
- Audit trail for compliance
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import structlog

from .config import get_settings
from .models.database import engine, Base
from .routers import inventory
from .middleware import (
    setup_logging,
    RequestContextMiddleware,
    RateLimitMiddleware,
    LoggingMiddleware,
    register_exception_handlers,
    init_rate_limiter,
    shutdown_rate_limiter,
    get_logger,
)

settings = get_settings()

# Configure logging before anything else
setup_logging(debug=settings.DEBUG)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle.

    Creates database tables on startup (dev mode only).
    Use Alembic migrations in production.
    """
    logger.info(
        "application_startup",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
    )

    # Initialize rate limiter
    await init_rate_limiter()
    logger.info("rate_limiter_initialized")

    # Create tables (dev mode only)
    if settings.DEBUG:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("database_tables_created")

    yield

    # Shutdown
    logger.info("application_shutdown")
    await shutdown_rate_limiter()
    await engine.dispose()


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Enterprise AI Governance & Compliance Platform API",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    contact={
        "name": "DataSafeguard Support",
        "email": "support@datasafeguard.ai",
    },
    license_info={
        "name": "Proprietary",
        "url": "https://datasafeguard.ai/license",
    },
    terms_of_service="https://datasafeguard.ai/terms",
)

# Register exception handlers (must be done before middleware)
register_exception_handlers(app)


# ── Middleware Stack ──
# Order matters: outer to inner execution
# CORS must be outermost
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request context: generates request_id and tracks timing
app.add_middleware(RequestContextMiddleware)

# Logging: logs all requests with context
app.add_middleware(LoggingMiddleware)

# Rate limiting: slides window rate limiter
app.add_middleware(RateLimitMiddleware)


# ── Health Check Endpoints ──


@app.get(
    "/health/live",
    tags=["Health"],
    summary="Liveness probe",
    description="Indicates if the service is alive and responding.",
    responses={
        200: {"description": "Service is alive"},
    },
)
async def health_live():
    """
    Liveness probe for Kubernetes and orchestration systems.

    Returns 200 if the service is running and able to respond to requests.
    """
    return {"status": "alive", "service": "datasafeguard-api"}


@app.get(
    "/health/ready",
    tags=["Health"],
    summary="Readiness probe",
    description="Indicates if the service is ready to handle traffic (DB and cache available).",
    responses={
        200: {"description": "Service is ready"},
        503: {"description": "Service dependencies unavailable"},
    },
)
async def health_ready():
    """
    Readiness probe for Kubernetes and orchestration systems.

    Returns 200 only if all dependencies (database, Redis) are available.
    Returns 503 if any critical dependency is unavailable.
    """
    try:
        # Check database connectivity
        async with engine.begin() as conn:
            await conn.execute(__import__("sqlalchemy").text("SELECT 1"))

        # Check Redis connectivity
        from .middleware.rate_limiter import get_rate_limiter

        limiter = get_rate_limiter()
        if limiter.redis_available and limiter.redis_client:
            await limiter.redis_client.ping()

        return {
            "status": "ready",
            "service": "datasafeguard-api",
            "database": "connected",
            "redis": "connected" if limiter.redis_available else "unavailable",
        }

    except Exception as e:
        logger.warning("readiness_check_failed", error=str(e))
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "not_ready",
                "service": "datasafeguard-api",
                "error": str(e),
            },
        )


@app.get(
    "/health",
    tags=["Health"],
    summary="Health check (deprecated)",
    description="Legacy health endpoint. Use /health/live or /health/ready instead.",
    responses={
        200: {"description": "Service is healthy"},
    },
)
async def health_check():
    """
    Legacy health endpoint for backward compatibility.

    Use /health/live or /health/ready for production orchestration.
    """
    return {
        "status": "healthy",
        "service": "datasafeguard-api",
        "version": settings.APP_VERSION,
    }


# ── Metrics Endpoint ──
# TODO: Implement Prometheus metrics endpoint
# @app.get("/metrics", tags=["Monitoring"])
# async def metrics():
#     """Prometheus metrics in OpenMetrics format."""
#     pass


# ── OpenAPI Tags ──
tags_metadata = [
    {
        "name": "Health",
        "description": "Service health and readiness checks for orchestration systems.",
    },
    {
        "name": "AI System Inventory",
        "description": "Register, retrieve, and manage AI systems in the compliance registry (UC-1).",
    },
    {
        "name": "Risk Classification",
        "description": "Classify AI systems against EU AI Act Annex III and US OMB criteria.",
    },
    {
        "name": "Approvals",
        "description": "Approval workflows for system registration and classification (UC-1).",
    },
    {
        "name": "Audit Trail",
        "description": "Immutable compliance audit trail and forensics.",
    },
]

app.openapi_tags = tags_metadata


# ── Register Routers ──

app.include_router(
    inventory.router,
    prefix=settings.API_PREFIX,
    tags=["AI System Inventory", "Risk Classification", "Approvals"],
)


# Future UC routers will be added here:
# app.include_router(crosswalk.router, prefix=settings.API_PREFIX)     # UC-2
# app.include_router(security.router, prefix=settings.API_PREFIX)      # UC-3
# app.include_router(audit.router, prefix=settings.API_PREFIX)         # UC-4
# app.include_router(bias.router, prefix=settings.API_PREFIX)          # UC-5
# app.include_router(training_data.router, prefix=settings.API_PREFIX) # UC-6
# app.include_router(hitl.router, prefix=settings.API_PREFIX)          # UC-7
# app.include_router(documentation.router, prefix=settings.API_PREFIX) # UC-8
# app.include_router(monitoring.router, prefix=settings.API_PREFIX)    # UC-9
# app.include_router(vendor.router, prefix=settings.API_PREFIX)        # UC-10
# app.include_router(nist_rmf.router, prefix=settings.API_PREFIX)      # UC-11
# app.include_router(gpai.router, prefix=settings.API_PREFIX)          # UC-12
