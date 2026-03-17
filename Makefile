.PHONY: help dev dev-full stop build logs api-logs test test-local lint format migrate migrate-new db-shell redis-cli clean

# Default target
.DEFAULT_GOAL := help

# ── Core Development ──

dev: ## Start core services (postgres, redis, api, frontend, nginx)
	docker compose up -d

dev-full: ## Start all services including monitoring (Prometheus + Jaeger)
	docker compose --profile monitoring up -d

stop: ## Stop all running services
	docker compose down

build: ## Build Docker images
	docker compose build

clean: ## Remove all containers and volumes (including data)
	docker compose down -v

logs: ## View logs from all services
	docker compose logs -f

api-logs: ## View logs from API service
	docker compose logs -f api

# ── Individual Service Development ──

api: ## Run API service locally (development mode)
	cd services/api-gateway && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

frontend: ## Run frontend service locally (development mode)
	cd frontend && npm run dev

# ── Database Management ──

db-shell: ## Open PostgreSQL shell
	docker compose exec postgres psql -U datasafeguard -d datasafeguard

redis-cli: ## Open Redis CLI
	docker compose exec redis redis-cli

migrate: ## Run database migrations (Alembic)
	docker compose exec api alembic upgrade head

migrate-new: ## Create a new database migration (requires NAME variable)
	@if [ -z "$(NAME)" ]; then \
		echo "Error: NAME variable is required. Usage: make migrate-new NAME='add_users_table'"; \
		exit 1; \
	fi
	docker compose exec api alembic revision --autogenerate -m "$(NAME)"

# ── Testing ──

test: ## Run backend tests in Docker container
	docker compose exec api python -m pytest tests/ -v

test-local: ## Run backend tests locally
	cd services/api-gateway && python -m pytest tests/ -v

test-coverage: ## Run tests with coverage report
	cd services/api-gateway && python -m pytest tests/ -v --cov=app --cov-report=html

# ── Code Quality ──

lint: ## Run linting (Ruff for Python, ESLint for TypeScript)
	cd services/api-gateway && ruff check app/
	cd frontend && npm run lint

format: ## Format code (Ruff for Python, Prettier for TypeScript)
	cd services/api-gateway && ruff format app/
	cd frontend && npm run format || npm run lint -- --fix

# ── Help ──

help: ## Display this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "%-20s %s\n", $$1, $$2}'
