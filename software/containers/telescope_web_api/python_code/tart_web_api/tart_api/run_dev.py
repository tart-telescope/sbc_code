#!/usr/bin/env python3
"""
Development startup script for TART FastAPI application.

This script starts the FastAPI application in development mode with hot reload.
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "tart_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        reload_dirs=["app"],
    )
