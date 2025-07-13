"""
TART FastAPI application module.

This module contains the FastAPI application for the TART telescope web API,
providing a modern async interface while maintaining compatibility with the
existing Flask-based system.
"""

from .main import app

__all__ = ["app"]
