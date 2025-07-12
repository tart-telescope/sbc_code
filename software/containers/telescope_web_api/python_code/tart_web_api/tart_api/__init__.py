"""
TART FastAPI Application Package.

This package provides a FastAPI-based web API for the TART telescope system,
maintaining compatibility with the existing Flask-based API while providing
modern async capabilities.
"""

__version__ = "0.1.0"
__all__ = ["app"]

from .app import app
