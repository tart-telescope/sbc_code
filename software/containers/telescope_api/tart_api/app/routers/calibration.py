"""
Calibration router for TART telescope API.

This module provides calibration endpoints that reuse the existing
Flask calibration logic while providing FastAPI-compatible responses.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from database import AsyncDatabase, get_database
from generated_models.calibration_models import (
    GetGainResponse,
    SetAntennaPositionsRequest,
    SetGainRequest,
)
from generated_models.common_models import EmptyResponse

from ..dependencies import AuthDep, ConfigDep

router = APIRouter()


@router.post("/gain", response_model=EmptyResponse)
async def set_gain(
    gain_request: SetGainRequest,
    config: ConfigDep,
    _: AuthDep,
    db: Annotated[AsyncDatabase, Depends(get_database)],
):
    """
    Set channel based complex gains.

    This endpoint reuses the existing Flask logic for gain calibration.
    Requires JWT authentication.
    """
    await db.insert_gain(gain_request.gain, gain_request.phase_offset)
    return EmptyResponse()


@router.post("/antenna_positions", response_model=EmptyResponse)
async def set_calibration_antenna_positions(
    antenna_positions: SetAntennaPositionsRequest | list[list[float]],
    config: ConfigDep,
    _: AuthDep,
):
    """
    Set antenna positions.

    This endpoint reuses the existing Flask logic for antenna position calibration.
    Supports both new format: {"antenna_positions": [...]} and legacy format: [[1,2,3],[4,5,6],...].
    Requires JWT authentication.
    """
    # Handle both formats: new structured format and legacy array format
    if isinstance(antenna_positions, SetAntennaPositionsRequest):
        # New format: {"antenna_positions": [...]}
        raw_positions = [pos.root for pos in antenna_positions.antenna_positions]
    elif isinstance(antenna_positions, list):
        # Legacy format: [[1,2,3],[4,5,6],...]
        raw_positions = antenna_positions
    else:
        raise HTTPException(status_code=422, detail="Invalid antenna positions format")

    config["antenna_positions"] = raw_positions
    return EmptyResponse()


@router.get("/gain", response_model=GetGainResponse)
async def get_gain(config: ConfigDep, db: Annotated[AsyncDatabase, Depends(get_database)]):
    """
    Get channel based complex gains.

    This endpoint reuses the existing Flask logic for gain retrieval.
    """
    num_ant = config["telescope_config"]["num_antenna"]
    rows_dict = await db.get_gain()

    ret_gain = [rows_dict[i][2] for i in range(num_ant)]
    ret_ph = [rows_dict[i][3] for i in range(num_ant)]

    return GetGainResponse(gain=ret_gain, phase_offset=ret_ph)
