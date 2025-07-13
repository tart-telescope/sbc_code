.PHONY: help build up down codegen clean format check

help:
	@echo "Available targets:"
	@echo "  build    - Build all containers"
	@echo "  up       - Start development environment"
	@echo "  down     - Stop development environment"
	@echo "  codegen  - Generate Pydantic models from schemas"
	@echo "  clean    - Clean up containers and volumes"
	@echo "  format   - Format code with ruff"
	@echo "  check    - Type check with ty"

build:
	docker compose -f compose.yml build

up:
	docker compose -f compose.yml up --build

down:
	docker compose -f compose.yml down

codegen:
	docker compose -f compose.yml --profile codegen run --rm codegen

clean:
	docker compose -f compose.yml down -v --remove-orphans
	docker system prune -f

format:
	docker compose -f compose.yml exec tart-api uv run ruff check --fix

check:
	docker compose -f compose.yml exec tart-api uvx ty check --output-format concise
