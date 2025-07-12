"""
Operation router for TART telescope API.

This module provides telescope operation control endpoints that reuse the existing
Flask operation logic while providing FastAPI-compatible responses.
"""

from fastapi import APIRouter, HTTPException, status

from models.operation_models import (
    AvailableModesResponse,
    CurrentModeResponse,
    SetLoopModeResponse,
    SetModeResponse,
)

from ..dependencies import AuthDep, ConfigDep

router = APIRouter()


@router.get("/mode/current", response_model=CurrentModeResponse)
async def get_current_mode(config: ConfigDep):
    """
    Get current telescope operating mode.

    This endpoint reuses the existing Flask logic for mode reporting.
    """
    return CurrentModeResponse(mode=config["mode"])


@router.get("/mode", response_model=AvailableModesResponse)
async def get_mode(config: ConfigDep):
    """
    Get available telescope operating modes.

    This endpoint reuses the existing Flask logic for available modes.
    """
    return AvailableModesResponse(modes=config["modes_available"])


@router.post("/mode/{mode}", response_model=SetModeResponse)
async def set_mode(mode: str, config: ConfigDep, _: AuthDep):
    """
    Set telescope operating mode.

    This endpoint reuses the existing Flask logic for mode setting.
    Requires JWT authentication.
    """
    if mode in config["modes_available"]:
        config["mode"] = mode
        return SetModeResponse(mode=config["mode"])
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid mode. Available modes: {config['modes_available']}",
        )


@router.post("/loop/{loop_mode}", response_model=SetLoopModeResponse)
async def set_loop_mode(loop_mode: str, config: ConfigDep, _: AuthDep):
    """
    Set telescope loop mode.

    This endpoint reuses the existing Flask logic for loop mode setting.
    Requires JWT authentication.
    """
    if loop_mode in config["loop_mode_available"]:
        config["loop_mode"] = loop_mode
        return SetLoopModeResponse(loop_mode=config["loop_mode"])
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid loop mode. Available modes: {config['loop_mode_available']}",
        )


@router.post("/loop/count/{loop_n}", response_model=SetLoopModeResponse)
async def set_loop_n(loop_n: int, config: ConfigDep, _: AuthDep):
    """
    Set telescope loop count.

    This endpoint reuses the existing Flask logic for loop count setting.
    Requires JWT authentication.

    Note: There's a bug in the original Flask code where it uses `loop_mode`
    instead of `loop_n`. We fix that here.
    """
    if 0 <= loop_n <= 100:
        config["loop_n"] = loop_n  # Fixed: was loop_mode in Flask
        return SetLoopModeResponse(loop_mode=config["loop_mode"])
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Loop count must be between 0 and 100",
        )
