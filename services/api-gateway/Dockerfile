# ── Stage 1: Builder ──
FROM python:3.12-slim as builder

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# ── Stage 2: Production ──
FROM python:3.12-slim

WORKDIR /app

LABEL maintainer="DataSafeguard Team <team@datasafeguard.ai>"
LABEL version="0.1.0"
LABEL description="DataSafeguard AI Governance Platform - API Gateway"

# Copy installed packages from builder
COPY --from=builder /root/.local /home/appuser/.local

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Set PATH to include user site-packages
ENV PATH=/home/appuser/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Copy application code
COPY --chown=appuser:appuser . .

EXPOSE 8000

# Health check
HEALTHCHECK --interval=10s --timeout=5s --retries=5 --start-period=20s \
    CMD curl -f http://localhost:8000/health/live || exit 1

# Default production command with gunicorn + uvicorn workers
ENV WORKERS=4
CMD ["sh", "-c", "gunicorn app.main:app --workers $WORKERS --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --timeout 120 --access-logfile - --error-logfile -"]
