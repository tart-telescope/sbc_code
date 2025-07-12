"""
FastAPI main application entry point for TART telescope web API.

This module creates the FastAPI application and includes all routers.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import init_database
from services import cleanup_telescope_service, init_telescope_service

from .config import init_config
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

    # Start telescope control service (state machine)
    await init_telescope_service(config._config)

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
async def health_check():
    """Health check endpoint with telescope service status."""
    try:
        from services import get_telescope_service

        service = await get_telescope_service()
        telescope_status = service.get_status()

        # Overall health is healthy if service is running
        overall_status = "healthy" if telescope_status["service_running"] else "degraded"

        return {"status": overall_status, "telescope_service": telescope_status}
    except Exception as e:
        return {
            "status": "degraded",
            "telescope_service": {"error": str(e)},
            "message": "Telescope service not available",
        }
