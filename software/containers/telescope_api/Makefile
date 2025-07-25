.PHONY: help build up down dev-reload codegen clean format check test test-clean test-schema setup-buildx bake-local bake-all bake-cross bake-inspect inspect-manifest

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
	@echo "  setup-buildx - Setup Docker buildx for cross-platform builds"
	@echo "  bake-local - Build local image (amd64 only)"
	@echo "  bake-all   - Build all platforms (amd64, arm/v6, arm/v7, arm64)"
	@echo "  bake-cross - Build and push all platforms with cache"
	@echo "  bake-inspect - Show bake targets and configuration"
	@echo "  inspect-manifest - Show platform information for built images"

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

setup-buildx:
	docker buildx create --name multiarch --driver docker-container --use --bootstrap || docker buildx use multiarch

bake-local: setup-buildx
	docker buildx bake --load

bake-all: setup-buildx
	docker buildx bake image-all

bake-cross: setup-buildx
	docker buildx bake image-cross --push

bake-inspect:
	@echo "=== Available Bake Targets ==="
	docker buildx bake --print
	@echo ""
	@echo "=== All Platforms Target ==="
	docker buildx bake --print image-all

inspect-manifest:
	@echo "=== Local telescope-api:local ==="
	docker buildx imagetools inspect telescope-api:local 2>/dev/null || echo "Local image not found"
	@echo ""
	@echo "=== Registry ghcr.io/tart-telescope/sbc_code:latest ==="
	docker buildx imagetools inspect ghcr.io/tart-telescope/sbc_code:latest 2>/dev/null || echo "Registry image not found or not accessible"
	@echo ""
	@echo "=== Expected platforms: linux/amd64, linux/arm/v6, linux/arm/v7, linux/arm64 ==="
