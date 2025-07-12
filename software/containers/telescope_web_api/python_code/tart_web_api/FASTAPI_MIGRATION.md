# FastAPI Migration Plan

## Overview
Create a new `tart_api` folder with a FastAPI-based application that replicates the functionality of the existing Flask app while using the generated Pydantic v2 models.

## Project Structure
```
tart_api/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Configuration management
│   ├── dependencies.py      # Dependency injection
│   └── routers/
│       ├── __init__.py
│       ├── auth.py          # Authentication endpoints
│       ├── status.py        # Status monitoring endpoints
│       ├── operation.py     # Mode and loop control
│       ├── imaging.py       # Imaging data endpoints
│       ├── info.py          # Telescope info endpoint
│       ├── calibration.py   # Calibration endpoints
│       ├── channel.py       # Channel management
│       ├── acquisition.py   # Data acquisition endpoints
│       └── data.py          # Raw/vis data endpoints
├── models/                  # Symlink to ../generated_models
├── database/
│   ├── __init__.py
│   └── connection.py        # Database connection wrapper
├── middleware/
│   ├── __init__.py
│   ├── cors.py              # CORS middleware
│   └── auth.py              # JWT authentication middleware
├── services/
│   ├── __init__.py
│   ├── telescope.py         # Telescope control service
│   └── data_processing.py   # Data processing utilities
├── tests/
│   ├── __init__.py
│   ├── test_endpoints.py
│   └── test_models.py
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

## Migration Strategy

### Phase 1: Core Setup
- [x] Create project structure
- [ ] Set up pyproject.toml with FastAPI dependencies + ruff + ty
- [ ] Create symbolic link to generated_models
- [ ] Implement basic FastAPI app structure with ruff formatting
- [ ] Add CORS middleware
- [ ] Configure ruff for linting and formatting
- [ ] Configure ty for type checking

### Phase 2: Authentication
- [ ] Port JWT authentication from Flask-JWT-Extended to FastAPI
- [ ] Create authentication middleware
- [ ] Implement login/refresh endpoints using generated models
- [ ] Add dependency injection for protected routes

### Phase 3: Core Endpoints (High Priority)
- [ ] **Status endpoints** (`/status/*`)
  - Port FPGA status logic
  - Port channel status logic
  - Use generated status models for responses
- [ ] **Operation endpoints** (`/mode/*`, `/loop/*`)
  - Port mode control logic
  - Port loop control logic
  - Use generated operation models
- [ ] **Info endpoint** (`/info`)
  - Port telescope info logic
  - Use generated info models

### Phase 4: Data Endpoints (Medium Priority)
- [ ] **Imaging endpoints** (`/imaging/*`)
  - Port visibility data logic
  - Port antenna position logic
  - Port timestamp logic
  - Use generated imaging models
- [ ] **Calibration endpoints** (`/calibration/*`)
  - Port gain calibration logic
  - Port antenna position calibration
  - Use generated calibration models
- [ ] **Channel endpoints** (`/channel/*`)
  - Port channel management logic
  - Use generated channel models

### Phase 5: Acquisition & Data (Low Priority)
- [ ] **Acquisition endpoints** (`/acquire/*`)
  - Port acquisition control logic
  - Use generated acquisition models
- [ ] **Data endpoints** (`/raw/data`, `/vis/data`)
  - Port file handling logic
  - Use generated data models

### Phase 6: API Compatibility Testing
- [ ] **Schema Validation Suite**
  - Create endpoint-by-endpoint comparison tests
  - Validate request/response schemas match exactly
  - Test all 30 endpoints with identical inputs
  - Generate compatibility report
- [ ] **Breaking Change Detection**
  - Compare response data structures (JSON schema validation)
  - Allow improved HTTP status codes (document changes)
  - Validate error message formats (improvements allowed)
  - Test edge cases and error conditions
- [ ] **Automated Testing Pipeline**
  - Run Flask app on port 5000
  - Run FastAPI app on port 8000
  - Execute identical requests against both
  - Compare responses programmatically



## Technical Considerations

### Dependencies
```toml
[project]
dependencies = [
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "pydantic>=2.0.0",
    "python-jose[cryptography]>=3.3.0",  # JWT handling
    "python-multipart>=0.0.6",  # Form data
    "sqlalchemy>=2.0.0",  # Database ORM
    "asyncpg>=0.29.0",  # PostgreSQL async driver
    "redis>=5.0.0",  # Caching
]

[tool.ruff]
target-version = "py313"
line-length = 88
select = ["E", "W", "F", "I", "N", "B", "UP", "C4", "T20"]
ignore = ["E501"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"

[tool.ty]
# Type checking configuration
```

### Database Integration
- Wrap existing database functions in async/await
- Use SQLAlchemy 2.0+ async patterns
- Maintain compatibility with existing database schema

### Configuration Management
- Port Flask app config to Pydantic Settings
- Environment variable management
- Runtime configuration updates

### Service Layer
- Extract business logic from Flask views
- Create reusable service classes
- Implement dependency injection pattern

## Key Advantages of FastAPI Migration

### Core Benefits
- **Async/await support**: Better concurrency for I/O operations
- **Automatic validation**: Pydantic models validate requests/responses
- **Built-in OpenAPI**: Auto-generated API documentation

### Developer Experience
- **Type safety**: Full type hints with generated models + ty checking
- **Code quality**: Ruff formatting and linting from day one
- **Auto-completion**: IDE support for request/response models
- **Interactive docs**: Swagger UI and ReDoc out of the box
- **API Compatibility**: Automated testing ensures no breaking changes

### Maintainability
- **Dependency injection**: Clean separation of concerns
- **Automatic serialization**: No manual JSON handling
- **Built-in testing**: TestClient for easy endpoint testing

## Migration Steps

### Step 1: Create Basic Structure
```bash
mkdir tart_api
cd tart_api
# Create directory structure
# Set up pyproject.toml with ruff + ty
# Create symbolic link: ln -s ../generated_models models
# Run: uv run ruff check --fix
# Run: uvx ty check --output-format concise
```

### Step 2: Port Authentication
- Convert Flask-JWT-Extended to FastAPI JWT
- Create authentication dependencies
- Test login/refresh endpoints

### Step 3: Port Core Endpoints
- Start with `/status/fpga` (most complex)
- Port one endpoint at a time
- Test against original Flask responses

### Step 4: API Compatibility Testing
- **Create test suite**: `tests/test_api_compatibility.py`
- **Dual server testing**: Run both Flask and FastAPI simultaneously
- **Endpoint comparison**: Test all 30 endpoints with identical requests
- **Schema validation**: Ensure response structures match exactly
- **Breaking change detection**: Flag any differences for review


## Success Criteria

### Functional Parity
- [ ] All 30 endpoints working identically to Flask app
- [ ] Same response data structures (status codes may differ if improved)
- [ ] Same authentication behavior
- [ ] Same error handling
- [ ] **Zero data breaking changes** unless explicitly approved
- [ ] Comprehensive compatibility test suite passing



### Code Quality
- [ ] Full type safety with generated models + ty checking
- [ ] Ruff formatting and linting (zero warnings)
- [ ] Comprehensive test coverage (>90%)
- [ ] Auto-generated OpenAPI documentation
- [ ] Clean, maintainable code structure

## Timeline Estimate

- **Phase 1-2**: 2-3 days (Setup + Auth)
- **Phase 3**: 3-4 days (Core endpoints)
- **Phase 4**: 2-3 days (Data endpoints)
- **Phase 5**: 2-3 days (Acquisition endpoints)
- **Phase 6**: 2-3 days (Testing & validation)

**Total: 11-16 days**

## API Compatibility Testing Strategy

### Test Structure
```
tests/
├── test_api_compatibility.py    # Main compatibility test suite
├── test_data/
│   ├── sample_requests.json     # Test request data
│   └── expected_responses.json  # Expected response formats
├── utils/
│   ├── api_client.py           # HTTP client for both APIs
│   ├── schema_validator.py     # Response schema validation
│   └── diff_reporter.py        # Breaking change detection
└── reports/
    └── compatibility_report.md # Generated compatibility report
```

### Test Execution
```bash
# Start both servers
python -m tart_web_api.app &  # Flask on :5000
uvicorn tart_api.main:app --port 8000 &  # FastAPI on :8000

# Run compatibility tests
uv run pytest tests/test_api_compatibility.py -v
```

### Breaking Change Policy
- **Allowed**: Minor improvements (better error messages, additional fields, improved status codes)
- **Requires approval**: Data schema changes, removed fields
- **Forbidden**: Breaking existing client data integrations

## Notes

- Keep Flask app running during migration
- Use generated models as single source of truth
- Run `uv run ruff check --fix` after every change
- Run `uvx ty check --output-format concise` for type validation
- **Run compatibility tests after each endpoint migration**
- Maintain backward compatibility
- Focus on one endpoint group at a time
- Document any approved breaking changes