"""
Imaging router for TART telescope API.

This module provides imaging data endpoints that reuse the existing
Flask imaging logic while providing FastAPI-compatible responses.
"""

from datetime import UTC

import numpy as np
from fastapi import APIRouter

from models.imaging_models import (
    AntennaPositionsResponse,
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
        import os
        import sys

        sys.path.append(os.path.join(os.path.dirname(__file__), "../../../../tart_web_api"))
        import database as flask_db

        channel_list = flask_db.get_manual_channel_status()
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
    if "antenna_positions" in config:
        # Convert the antenna positions to the correct format
        positions = config["antenna_positions"]
        if positions and isinstance(positions[0], (list, tuple)):
            return AntennaPositionsResponse(positions)
        else:
            # Fallback to default positions
            return AntennaPositionsResponse([[0.0, 0.0, 0.0] for _ in range(24)])
    return AntennaPositionsResponse([[0.0, 0.0, 0.0] for _ in range(24)])


@router.get("/timestamp")
async def get_imaging_timestamp(config: ConfigDep):
    """
    Get timestamp of latest visibilities.

    This endpoint reuses the existing Flask logic for timestamp reporting.
    """
    from datetime import datetime

    if "vis_timestamp" in config:
        # Convert vis_timestamp to ISO string format
        from tart.util import utc

        return utc.to_string(config["vis_timestamp"])
    else:
        # Return current timestamp as ISO string
        return datetime.now(UTC).isoformat().replace("+00:00", "Z")
