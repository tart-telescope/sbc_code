"""
FastAPI main application entry point for TART telescope web API.

This module creates the FastAPI application and includes all routers.
"""

import logging
from contextlib import asynccontextmanager
from typing import Annotated, Any

from fastapi import Depends, FastAPI, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from database import init_database
from services import cleanup_telescope_service, init_telescope_service

from .config import init_config
from .dependencies import get_runtime_config
from .routers import (
    acquisition,
    auth,
    calibration,
    channel,
    data,
    imaging,
    info,
    operation,
    status,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and config on startup."""
    # Initialize configuration
    config = init_config()
    app.state.config = config

    # Initialize database
    num_ant = config["telescope_config"]["num_antenna"]
    await init_database(num_ant)

    # Set sample delay
    from database import get_database

    db = get_database()
    config["sample_delay"] = await db.get_sample_delay()

    # Load persisted sync settings into runtime config
    raw_config = config["raw"]
    persisted_sync = await db.get_setting("raw.sync")
    if persisted_sync is not None:
        raw_config["sync"] = persisted_sync
    persisted_sync_seconds = await db.get_setting("raw.sync_acquire_at_seconds")
    if persisted_sync_seconds is not None:
        raw_config["sync_acquire_at_seconds"] = persisted_sync_seconds
    config["raw"] = raw_config

    # Start telescope control service (state machine)
    await init_telescope_service(config)

    yield

    # Cleanup on shutdown
    await cleanup_telescope_service()


app = FastAPI(
    title="TART Telescope API",
    description="FastAPI-based web API for TART telescope control and data access",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(status.router, prefix="/status", tags=["status"])
app.include_router(operation.router, prefix="", tags=["operation"])
app.include_router(imaging.router, prefix="/imaging", tags=["imaging"])
app.include_router(info.router, prefix="/info", tags=["info"])
app.include_router(calibration.router, prefix="/calibration", tags=["calibration"])
app.include_router(channel.router, prefix="/channel", tags=["channel"])
app.include_router(acquisition.router, prefix="/acquire", tags=["acquisition"])
app.include_router(data.router, prefix="", tags=["data"])


@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {"message": "TART Telescope API", "status": "running"}


@app.get("/health")
async def health_check(
    request: Request,
    response: Response,
    config: Annotated[Any, Depends(get_runtime_config)],
):
    """Health check endpoint with telescope service status.

    Returns 503 when the telescope service is not running or an error
    occurred while checking it. Configuration degradations (e.g. a corrupted
    antenna positions file) are reported in degraded_reasons.
    """
    degraded_reasons = []

    if config is not None and config.get("antenna_positions_error"):
        degraded_reasons.append(f"antenna positions: {config['antenna_positions_error']}")

    try:
        from services import get_telescope_service

        service = await get_telescope_service()
        telescope_status = service.get_status()

        # Overall health is healthy if service is running
        service_running = telescope_status["service_running"]
        if not service_running:
            response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

        result = {
            "status": "healthy" if service_running and not degraded_reasons else "degraded",
            "telescope_service": telescope_status,
        }
        if degraded_reasons:
            result["degraded_reasons"] = degraded_reasons
        return result
    except Exception as e:
        logging.exception("Health check failed")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "degraded",
                "telescope_service": {"error": str(e)},
                "message": "Telescope service not available",
                "degraded_reasons": degraded_reasons,
            },
        )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Return a consistent JSON error for unexpected server errors."""
    # Let FastAPI handle its own HTTPException and validation errors
    if isinstance(exc, (StarletteHTTPException, RequestValidationError)):
        raise exc

    logging.exception("Unhandled error processing %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )
