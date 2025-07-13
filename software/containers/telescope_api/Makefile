.PHONY: help build up down dev-reload codegen clean format check test test-clean test-schema

help:
	@echo "Available targets:"
	@echo "  build      - Build all containers"
	@echo "  up         - Start development environment"
	@echo "  down       - Stop development environment"
	@echo "  dev-reload - Start with hot reload (experimental)"
	@echo "  codegen    - Generate Pydantic models from schemas"
	@echo "  test       - Run comprehensive API tests (isolated environment)"
	@echo "  test-clean - Clean up test environment"
	@echo "  test-schema- Check if generated models are up-to-date with schemas"
	@echo "  clean      - Clean up containers and volumes"
	@echo "  format     - Format code with ruff"
	@echo "  check      - Type check with ty"

build:
	docker compose -f compose.yml build

up:
	docker compose -f compose.yml up --build

down:
	docker compose -f compose.yml down

dev-reload:
	docker compose -f compose.yml run --rm -p 8000:5000 tart-api python -m uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload --reload-dir /app --use-colors

codegen:
	docker compose -f compose.yml --profile codegen run --rm codegen

test:
	docker compose -f compose.test.yml up --build test-runner --abort-on-container-exit

test-clean:
	docker compose -f compose.test.yml down -v --remove-orphans

test-schema:
	python3 test_schema_sync_standalone.py

clean:
	docker compose -f compose.yml down -v --remove-orphans
	docker system prune -f

format:
	docker compose -f compose.yml exec tart-api uv run ruff check --fix

check:
	docker compose -f compose.yml exec tart-api uvx ty check --output-format concise
