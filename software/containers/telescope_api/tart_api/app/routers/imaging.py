"""
Imaging router for TART telescope API.

This module provides imaging data endpoints that reuse the existing
Flask imaging logic while providing FastAPI-compatible responses.
"""

import numpy as np
from fastapi import APIRouter, HTTPException

from generated_models.imaging_models import (
    AntennaPositionsResponse,
    AntennaPositionsResponseItem,
    VisibilityResponse,
)

from ..dependencies import ConfigDep

router = APIRouter()


@router.get("/vis", response_model=VisibilityResponse)
async def get_latest_vis(config: ConfigDep):
    """
    Get latest visibilities.

    This endpoint reuses the existing Flask logic for visibility data,
    including filtering by enabled channels.
    """
    if "vis_current" in config:
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
    else:
        # Return empty visibility response when no data available
        return VisibilityResponse(data=[])


@router.get("/antenna_positions", response_model=AntennaPositionsResponse)
async def get_imaging_antenna_positions(config: ConfigDep):
    """
    Get antenna positions.

    This endpoint reuses the existing Flask logic for antenna position reporting.
    """
    positions = config["antenna_positions"]
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
