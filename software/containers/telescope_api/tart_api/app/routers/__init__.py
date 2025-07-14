"""
FastAPI routers module for TART telescope API.

This module contains all the API route handlers organized by functionality.
Each router handles a specific group of endpoints while maintaining compatibility
with the existing Flask API structure.
"""

from . import (
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

__all__ = [
    "acquisition",
    "auth",
    "calibration",
    "channel",
    "data",
    "imaging",
    "info",
    "operation",
    "status",
]
