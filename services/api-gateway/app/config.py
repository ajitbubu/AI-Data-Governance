"""Application configuration loaded from environment variables."""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings with support for environment variable configuration."""

    # Application
    APP_NAME: str = "DataSafeguard API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    API_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"
    """Environment: development, staging, or production"""

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://datasafeguard:datasafeguard@localhost:5432/datasafeguard"
    DATABASE_ECHO: bool = False

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Auth
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    AUTH_SECRET_KEY: str = "dev-jwt-secret-key-change-in-production"
    AUTH_DEV_BYPASS: bool = True
    """Enable dev mode bypass for testing (default: True for development)"""

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALGORITHM: str = "HS256"

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    """Default rate limit for read endpoints: requests per minute"""

    RATE_LIMIT_WRITE_PER_MINUTE: int = 20
    """Rate limit for write endpoints: requests per minute"""

    # Logging
    LOG_LEVEL: str = "INFO"
    """Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL"""

    LOG_FORMAT: str = "json"
    """Log format: json for production, console for development"""

    # OpenTelemetry
    OTEL_ENABLED: bool = False
    """Enable OpenTelemetry instrumentation"""

    OTEL_SERVICE_NAME: str = "datasafeguard-api"
    """Service name for OpenTelemetry traces"""

    OTEL_EXPORTER_ENDPOINT: str = "http://jaeger:4317"
    """OTLP exporter endpoint (e.g., Jaeger collector)"""

    # Classification
    CLASSIFICATION_CONFIDENCE_THRESHOLD: float = 0.75
    ANNEX_III_SIMILARITY_THRESHOLD: float = 0.70

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Returns:
        Singleton Settings object
    """
    return Settings()
