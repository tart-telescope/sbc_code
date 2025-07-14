# TART Telescope API

Modern FastAPI-based telescope control system with schema-first development.

## Schema-First Approach

1. **JSON Schemas** define API contracts in `schemas/`
2. **Pydantic Models** auto-generated from schemas via `make codegen`
3. **Type Safety** enforced throughout the application
4. **API Documentation** auto-generated from models

## Quick Start

```bash
# Generate models from schemas
make codegen

# Start development environment
make up

# API docs: http://localhost:8000/docs
# Web UI: http://localhost:8080
```

## Automated Documentation

The API automatically generates interactive documentation from Pydantic models:
- **Swagger UI** at `/docs` - Interactive API explorer
- **ReDoc** at `/redoc` - Clean documentation format
- **OpenAPI Schema** at `/openapi.json` - Machine-readable spec

All request/response schemas are validated and documented without manual effort.

## Requirements

These files must exist in parent directory:
- `../../telescope_config.json` - Telescope configuration
- `../../calibrated_antenna_positions.json` - Antenna positions

## Commands

```bash
make codegen    # Generate Pydantic models from schemas
make up         # Start development environment
make test       # Run test suite
make down       # Stop environment
```

## Architecture

- **FastAPI** - Async web framework
- **Pydantic v2** - Type-safe models from JSON schemas
- **JWT Auth** - Compatible with existing Flask tokens
- **Docker** - Containerized development and deployment
- **Background Services** - Telescope state machine, data processing

## Testing

Comprehensive test suite ensures API compatibility:
- 16 endpoint tests
- Isolated test environment

The API is a drop-in replacement for the existing Flask implementation.
