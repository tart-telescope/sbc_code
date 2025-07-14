"""
Services module for TART FastAPI application.

This module provides background services for telescope control, data processing,
and hardware interface management while maintaining compatibility with the
existing Flask-based system.
"""

from .telescope_control import (
    TelescopeControlService,
    cleanup_telescope_service,
    get_telescope_service,
    init_telescope_service,
)

__all__ = [
    "TelescopeControlService",
    "get_telescope_service",
    "init_telescope_service",
    "cleanup_telescope_service",
]
