"""
Data router for TART telescope API.

This module provides data file endpoints that reuse the existing
Flask data logic while providing FastAPI-compatible responses.
"""

from typing import Annotated

from fastapi import APIRouter, Depends

from database import AsyncDatabase, get_database
from generated_models.data_models import RawDataResponse, VisDataResponse

from ..dependencies import ConfigDep

router = APIRouter()


@router.get("/raw/data", response_model=RawDataResponse)
async def get_raw_data_file_handles(
    config: ConfigDep, db: Annotated[AsyncDatabase, Depends(get_database)]
):
    """
    Get list of latest raw data files.

    This endpoint reuses the existing Flask logic for raw data file listing.
    """
    data_root = config["data_root"]
    ret = await db.get_raw_file_handle()

    # Apply same processing as Flask app
    for el in ret:
        el["filename"] = el["filename"][len(data_root) + 1 :]
        # Convert datetime to string if needed
        if hasattr(el["timestamp"], "isoformat"):
            el["timestamp"] = el["timestamp"].isoformat()
        # Remove extra fields that aren't in the model
        el.pop("Id", None)

    return RawDataResponse(ret)


@router.get("/vis/data", response_model=VisDataResponse)
async def get_vis_data_file_handles(
    config: ConfigDep, db: Annotated[AsyncDatabase, Depends(get_database)]
):
    """
    Get list of latest visibility data files.

    This endpoint reuses the existing Flask logic for visibility data file listing.
    """
    data_root = config["data_root"]
    ret = await db.get_vis_file_handle()

    # Apply same processing as Flask app
    for el in ret:
        el["filename"] = el["filename"][len(data_root) + 1 :]
        # Convert datetime to string if needed
        if hasattr(el["timestamp"], "isoformat"):
            el["timestamp"] = el["timestamp"].isoformat()
        # Remove extra fields that aren't in the model
        el.pop("Id", None)

    return VisDataResponse(ret)
