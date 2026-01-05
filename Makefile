.PHONY: help install install-dev run start start-docs test lint format type-check security-check ci-check pre-commit clean docker-check docker-up docker-down docker-up-prod docker-down-prod docker-build docker-logs docker-logs-prod docker-ps docker-restart docker-clean env env-copy env-show env-update celery celery-beat celery-flower redis-cli

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install production dependencies
	poetry install --no-dev

install-dev: ## Install all dependencies including dev
	poetry install --with dev
	poetry run pre-commit install

run: ## Run development server
	poetry run uvicorn app.app:app --reload --host 0.0.0.0 --port 8000

start: ## Start app and open docs automatically
	@echo "🚀 Starting FastAPI server..."
	@echo ""
	@echo "📚 API Documentation:"
	@echo "   Swagger UI:  http://localhost:8000/docs"
	@echo "   ReDoc:       http://localhost:8000/redoc"
	@echo "   OpenAPI:     http://localhost:8000/openapi.json"
	@echo ""
	@echo "💡 The docs will open in your browser shortly..."
	@echo "   Press Ctrl+C to stop the server"
	@echo ""
	@sleep 3 && (open http://localhost:8000/docs 2>/dev/null || xdg-open http://localhost:8000/docs 2>/dev/null || start http://localhost:8000/docs 2>/dev/null || true) &
	poetry run uvicorn app.app:app --reload --host 0.0.0.0 --port 8000

start-docs: ## Open API documentation in browser
	@echo "Opening API docs..."
	@open http://localhost:8000/docs 2>/dev/null || xdg-open http://localhost:8000/docs 2>/dev/null || start http://localhost:8000/docs 2>/dev/null || echo "Please visit http://localhost:8000/docs in your browser"

test: ## Run tests
	poetry run pytest -v

test-cov: ## Run tests with coverage
	poetry run pytest --cov=app --cov-report=html --cov-report=term -v

lint: ## Run linters (ruff, mypy)
	poetry run ruff check app tests
	poetry run mypy app || true

format: ## Format code (black, isort, ruff)
	poetry run black app tests
	poetry run isort app tests
	poetry run ruff format app tests

format-check: ## Check code formatting without making changes
	poetry run black --check app tests
	poetry run isort --check-only app tests
	poetry run ruff format --check app tests

type-check: ## Run type checker
	poetry run mypy app

security-check: ## Run security checks (bandit)
	poetry run bandit -r app/ -f json -o bandit-report.json

ci-check: ## Run all CI checks (lint, format-check, type-check, test, security-check)
	@echo "🔍 Running CI checks..."
	@echo ""
	@echo "📝 Checking code formatting..."
	@$(MAKE) format-check
	@echo ""
	@echo "🔎 Running linters..."
	@$(MAKE) lint
	@echo ""
	@echo "📊 Running type checker..."
	@$(MAKE) type-check || true
	@echo ""
	@echo "🧪 Running tests..."
	@$(MAKE) test
	@echo ""
	@echo "🔒 Running security checks..."
	@$(MAKE) security-check || true
	@echo ""
	@echo "✅ All CI checks completed!"

pre-commit: ## Run pre-commit hooks on all files
	poetry run pre-commit run --all-files

clean: ## Clean cache and temporary files
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} +
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -f bandit-report.json

docker-check: ## Check if Docker daemon is running
	@docker info > /dev/null 2>&1 || (echo "❌ Docker daemon is not running!" && \
		echo "💡 On macOS, start Docker Desktop from Applications" && \
		echo "💡 Or run: open -a Docker" && exit 1)
	@echo "✅ Docker daemon is running"

docker-up: docker-check ## Start Docker containers (dev dependencies only)
	docker compose -f docker-compose.dev.yml up -d

docker-down: ## Stop Docker containers (dev)
	docker compose -f docker-compose.dev.yml down

docker-up-prod: ## Start full production stack
	docker compose up -d

docker-down-prod: ## Stop production stack
	docker compose down

docker-build: ## Build Docker image
	docker compose build

docker-logs: ## View Docker logs (dev)
	docker compose -f docker-compose.dev.yml logs -f

docker-logs-prod: ## View Docker logs (production)
	docker compose logs -f

docker-ps: ## List running containers
	docker compose ps

docker-restart: ## Restart Docker containers (dev)
	docker compose -f docker-compose.dev.yml restart

docker-clean: ## Stop and remove containers, volumes, networks
	docker compose -f docker-compose.dev.yml down -v
	docker compose down -v

# Database Migrations (Alembic)
migration-create: ## Create a new migration (usage: make migration-create MESSAGE="description")
	poetry run alembic revision --autogenerate -m "$(MESSAGE)"

migration-upgrade: ## Apply all pending migrations
	poetry run alembic upgrade head

migration-downgrade: ## Rollback one migration
	poetry run alembic downgrade -1

migration-history: ## Show migration history
	poetry run alembic history

migration-current: ## Show current migration version
	poetry run alembic current

env: ## Show environment setup help
	@echo "Environment Management Commands:"
	@echo "  make env-copy    - Copy .env.example to .env (if .env doesn't exist)"
	@echo "  make env-update  - Update .env from .env.example (preserves existing values)"
	@echo "  make env-show    - Show current .env variables (secrets masked)"

env-copy: ## Copy .env.example to .env if .env doesn't exist
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✅ Created .env from .env.example"; \
		echo "⚠️  Please update .env with your actual values (especially SECRET_KEY)"; \
	else \
		echo "⚠️  .env already exists. Use 'make env-update' to refresh from .env.example"; \
	fi

env-update: ## Update .env from .env.example (merges new variables, preserves existing values)
	@if [ ! -f .env.example ]; then \
		echo "❌ .env.example not found!"; \
		exit 1; \
	fi; \
	if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✅ Created .env from .env.example"; \
	else \
		echo "🔄 Merging .env.example into .env..."; \
		cp .env .env.backup; \
		echo "📦 Backup created: .env.backup"; \
		{ \
			cat .env; \
			echo ""; \
			echo "# New variables from .env.example:"; \
			grep -v '^#' .env.example | grep -v '^$$' | while IFS='=' read -r key value; do \
				if [ -n "$$key" ]; then \
					if ! grep -q "^$$key=" .env.backup 2>/dev/null; then \
						echo "$$key=$$value"; \
					fi; \
				fi; \
			done; \
		} > .env.tmp && mv .env.tmp .env; \
		echo "✅ .env updated with new variables from .env.example"; \
		echo "✅ Existing values preserved"; \
		echo "📦 Backup saved to .env.backup"; \
	fi

env-show: ## Show current .env variables (secrets masked with ***)
	@if [ ! -f .env ]; then \
		echo "❌ .env file not found. Run 'make env-copy' first."; \
		exit 1; \
	fi; \
	echo "📋 Current .env variables:"; \
	echo ""; \
	grep -v '^#' .env | grep -v '^$$' | while IFS='=' read -r key value; do \
		if [ -n "$$key" ]; then \
			case "$$key" in \
				*SECRET*|*PASSWORD*|*KEY*|*TOKEN*) \
					echo "$$key=***"; \
					;; \
				*) \
					echo "$$key=$$value"; \
					;; \
			esac; \
		fi; \
	done

# Celery Commands
celery: ## Start Celery worker (for development)
	poetry run celery -A app.infrastructure.tasks.celery_app worker --loglevel=info

celery-beat: ## Start Celery beat scheduler (for development)
	poetry run celery -A app.infrastructure.tasks.celery_app beat --loglevel=info

celery-flower: ## Start Flower monitoring UI (http://localhost:5555)
	poetry run celery -A app.infrastructure.tasks.celery_app flower --port=5555

celery-purge: ## Purge all Celery tasks
	poetry run celery -A app.infrastructure.tasks.celery_app purge -f

# Redis Commands
redis-cli: ## Open Redis CLI (requires Redis running)
	docker exec -it app_redis_dev redis-cli

redis-flush: ## Flush all Redis data (WARNING: deletes all cached data)
	docker exec -it app_redis_dev redis-cli FLUSHALL
