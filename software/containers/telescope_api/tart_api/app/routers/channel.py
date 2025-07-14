"""
Channel router for TART telescope API.

This module provides channel management endpoints that reuse the existing
Flask channel logic while providing FastAPI-compatible responses.
"""

from typing import Annotated

from fastapi import APIRouter, Depends

from database import AsyncDatabase, get_database
from generated_models.channel_models import ChannelStatusResponse, ChannelToggleResponse

from ..dependencies import AuthDep

router = APIRouter()


@router.put("/{channel_idx}/{enable}", response_model=ChannelToggleResponse)
async def set_channel(
    channel_idx: int,
    enable: int,
    _: AuthDep,
    db: Annotated[AsyncDatabase, Depends(get_database)],
):
    """
    Enable/Disable channel manually.

    This endpoint reuses the existing Flask logic for channel management.
    Requires JWT authentication.
    """
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
