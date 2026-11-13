"""
Channel router for TART telescope API.

This module provides channel management endpoints that reuse the existing
Flask channel logic while providing FastAPI-compatible responses.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status

from database import AsyncDatabase, get_database
from generated_models.channel_models import ChannelStatusResponse, ChannelToggleResponse

from ..dependencies import AuthDep, ConfigDep

router = APIRouter()


@router.put(
    "/{channel_idx}/{enable}",
    response_model=ChannelToggleResponse,
    responses={
        404: {"description": "Channel not found"},
    },
)
async def set_channel(
    _: AuthDep,
    db: Annotated[AsyncDatabase, Depends(get_database)],
    config: ConfigDep,
    channel_idx: Annotated[int, Path(ge=0)],
    enable: Annotated[int, Path(ge=0, le=1)],
):
    """
    Enable/Disable channel manually.

    This endpoint reuses the existing Flask logic for channel management.
    Requires JWT authentication.
    Returns 404 if the channel index is out of range.
    """
    num_ant = config["telescope_config"]["num_antenna"]
    if not 0 <= channel_idx < num_ant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Channel {channel_idx} not found (telescope has {num_ant} channels)",
        )

    await db.update_manual_channel_status(channel_idx, bool(enable))
    return ChannelToggleResponse({str(channel_idx): enable})


@router.get("", response_model=ChannelStatusResponse)
async def get_all_channels(db: Annotated[AsyncDatabase, Depends(get_database)]):
    """
    Get all channels and their enabled/disabled status.

    This endpoint reuses the existing Flask logic for channel status retrieval.
    """
    ret = await db.get_manual_channel_status()
    return ChannelStatusResponse(ret)
