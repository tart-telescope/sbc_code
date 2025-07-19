# TART Telescope API

Modern FastAPI-based telescope control system with schema-first development.

## Hardware Interface
This python module in `hardware_interface` is responsible for communicating via SPI to the FPGA. It defines service loops for data capture,
processing, and control for the telescope control system.

## Telescope API
- A python app that models the telescope as a state machine
- A data model for the telescope's state and operations
- Provides a RESTful interface for monitoring and controlling the telescope's state
- Persisting gains and config state in a sqlite database
- Recording visibility and raw data HDF5 files, keeping a limited catalog and cleaning it up. (R/W)


## Schema-First Approach

1. **JSON Schemas** define API contracts in `schemas/`
2. **Pydantic Models** auto-generated from schemas via `make codegen`, outputs will be in `tart_api/generated_models/`
3. **Type Safety** enforced throughout the application
4. **API Documentation** auto-generated from models

## Quick Start

```bash
# Generate models from schemas
make codegen

# Start development environment
make up
# Web UI: http://localhost:8080
# API docs: http://localhost:8000/docs
# API docs: http://localhost:8000/
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
make up         # Start development environment
make test       # Run test suite
make down       # Stop environment
make codegen    # Generate Pydantic models from schemas
```

## Architecture

- **FastAPI** - Async web framework
- **Pydantic v2** - Type-safe models from JSON schemas
- **JWT Auth**
- **Docker** - Containerized development and deployment
- **Background Services** - Telescope state machine, data processing

## Testing

Comprehensive test suite ensures API compatibility:
- 16 endpoint tests
- Isolated test environment
