"""
Status router for TART telescope API.

This module provides status monitoring endpoints that reuse the existing
Flask status logic while providing FastAPI-compatible responses.
"""

from typing import Annotated

from fastapi import APIRouter, Depends

from database import AsyncDatabase, get_database
from generated_models.status_models import (
    StatusChannelAllResponse,
    StatusChannelSingleResponse,
    StatusFPGAResponse,
)

from ..dependencies import ConfigDep

router = APIRouter()


@router.get("/fpga", response_model=StatusFPGAResponse)
async def get_status_fpga(config: ConfigDep):
    """
    Get FPGA status information.

    This endpoint reuses the existing Flask logic for FPGA status reporting.
    Returns detailed hardware status including acquisition, SPI, and timing controller info.
    """
    if "status" in config:
        ret = dict(config["status"])
        ret["hostname"] = config["hostname"]

        # Fix timestamp field mapping
        if "timestamp (UTC)" in ret:
            ret["timestamp"] = ret.pop("timestamp (UTC)")
        elif "timestamp" not in ret:
            ret["timestamp"] = ""

        # Fix SYS_STATS.state enum value - clamp to 0-1 range
        if "SYS_STATS" in ret and "state" in ret["SYS_STATS"]:
            state_val = ret["SYS_STATS"]["state"]
            ret["SYS_STATS"]["state"] = 1 if state_val > 0 else 0

        return StatusFPGAResponse(**ret)
    else:
        # Return empty status with required fields when no status available
        return StatusFPGAResponse(
            hostname=config["hostname"],
            timestamp="",
            AQ_STREAM={"data": 0.0},
            AQ_SYSTEM={
                "512Mb": 0,
                "SDRAM_ready": 0,
                "enabled": 0,
                "error": 0,
                "overflow": 0,
                "state": 0,
            },
            SPI_STATS={"FIFO_overflow": 0, "FIFO_underrun": 0, "spi_busy": 0},
            SYS_STATS={
                "acq_en": 0,
                "cap_debug": 0,
                "cap_en": 0,
                "state": 0,
                "viz_en": 0,
                "viz_pend": 0,
            },
            TC_CENTRE={"centre": 0, "delay": 0, "drift": 0, "invert": 0},
            TC_DEBUG={"count": 0, "debug": 0, "numantenna": 24, "shift": 0},
            TC_STATUS={"delta": 0, "phase": 0},
            TC_SYSTEM={"enabled": 0, "error": 0, "locked": 0, "source": 0},
            VX_DEBUG={"limp": 0, "stuck": 0},
            VX_STATUS={"accessed": 0, "available": 0, "bank": 0, "overflow": 0},
            VX_STREAM={"data": 0},
            VX_SYSTEM={"blocksize": 0, "enabled": 0, "overwrite": 0},
        )


@router.get("/channel", response_model=StatusChannelAllResponse)
async def get_status_channel_all(
    config: ConfigDep, db: Annotated[AsyncDatabase, Depends(get_database)]
):
    """
    Get all channel status information.

    This endpoint reuses the existing Flask logic for channel status reporting,
    including enabled/disabled status from the database.
    """
    if "channels" in config:
        channel_list = await db.get_manual_channel_status()
        ret = list(config["channels"])

        # Apply the same logic as Flask app
        for ch in ret:
            # Find corresponding channel in database
            db_channel = next(
                (c for c in channel_list if c["channel_id"] == ch["id"]),
                {"enabled": True},
            )
            ch["enabled"] = db_channel["enabled"]

            # Apply same rounding as Flask
            if "phase" in ch and "stability" in ch["phase"]:
                ch["phase"]["stability"] = int(ch["phase"]["stability"] * 100) / 100.0
            if "radio_mean" in ch and "mean" in ch["radio_mean"]:
                ch["radio_mean"]["mean"] = int(ch["radio_mean"]["mean"] * 10000) / 10000.0

        return StatusChannelAllResponse(ret)
    else:
        return StatusChannelAllResponse([])


@router.get("/channel/{channel_idx}", response_model=StatusChannelSingleResponse)
async def get_status_channel_i(
    channel_idx: int,
    config: ConfigDep,
    db: Annotated[AsyncDatabase, Depends(get_database)],
):
    """
    Get specific channel status information.

    This endpoint reuses the existing Flask logic for individual channel status.
    """
    if "channels" in config:
        if 0 <= channel_idx < 24:
            channel_list = await db.get_manual_channel_status()
            ret = dict(config["channels"][channel_idx])

            # Find corresponding channel in database
            db_channel = next(
                (c for c in channel_list if c["channel_id"] == channel_idx),
                {"enabled": True},
            )
            ret["enabled"] = db_channel["enabled"]

            return StatusChannelSingleResponse(**ret)

    # Return empty channel response when channel not found
    return StatusChannelSingleResponse(
        id=channel_idx,
        enabled=0,
        phase={
            "N_samples": 0,
            "measured": 0.0,
            "ok": 0,
            "stability": 0.0,
            "threshold": 0.0,
        },
        radio_mean={"mean": 0.0, "ok": 0, "threshold": 0.0},
        freq=[],
        power=[],
    )
