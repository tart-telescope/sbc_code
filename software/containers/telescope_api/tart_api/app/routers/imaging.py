"""
Imaging router for TART telescope API.

This module provides imaging data endpoints that reuse the existing
Flask imaging logic while providing FastAPI-compatible responses.
"""

import numpy as np
from fastapi import APIRouter, HTTPException, status

from generated_models.imaging_models import (
    AntennaPositionsResponse,
    AntennaPositionsResponseItem,
    VisibilityResponse,
)

from ..dependencies import ConfigDep

router = APIRouter()


@router.get(
    "/vis",
    response_model=VisibilityResponse,
    responses={404: {"description": "No visibility data available"}},
)
async def get_latest_vis(config: ConfigDep):
    """
    Get latest visibilities.

    This endpoint reuses the existing Flask logic for visibility data,
    including filtering by enabled channels.
    Returns 404 if no visibility data has been acquired yet.
    """
    if "vis_current" not in config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No visibility data available",
        )

    ret = dict(config["vis_current"])

    # Import database functions to reuse channel filtering logic
    from database import get_database

    db = get_database()
    channel_list = await db.get_manual_channel_status()
    active_channels = np.zeros(len(channel_list))
    for ch in channel_list:
        active_channels[ch["channel_id"]] = ch["enabled"]

    active_vis = []
    for v in ret["data"]:
        if active_channels[v["i"]] and active_channels[v["j"]]:
            active_vis.append(v)
    ret["data"] = active_vis

    return VisibilityResponse(**ret)


@router.get(
    "/antenna_positions",
    response_model=AntennaPositionsResponse,
    responses={503: {"description": "Antenna positions unavailable (corrupted or missing calibration file)"}},
)
async def get_imaging_antenna_positions(config: ConfigDep):
    """
    Get antenna positions.

    This endpoint reuses the existing Flask logic for antenna position reporting.
    Returns 503 when antenna positions could not be loaded from
    calibrated_antenna_positions.json (see the error detail).
    """
    positions = config["antenna_positions"]
    if positions is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Antenna positions unavailable: {config.get('antenna_positions_error')}",
        )
    # Map raw positions to response model format
    response_items = [AntennaPositionsResponseItem(root=pos) for pos in positions]
    return AntennaPositionsResponse(root=response_items)


@router.get(
    "/timestamp",
    responses={404: {"description": "No visibility timestamp available"}},
)
async def get_imaging_timestamp(config: ConfigDep):
    """
    Get timestamp of latest visibilities.

    This endpoint reuses the existing Flask logic for timestamp reporting.
    Returns 404 if no visibility data is available.
    """
    if "vis_timestamp" in config:
        from tart.util import utc

        return utc.to_string(config["vis_timestamp"])
    else:
        raise HTTPException(status_code=404, detail="No visibility timestamp available")
