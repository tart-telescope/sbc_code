"""
Info router for TART telescope API.

This module provides telescope information endpoints that reuse the existing
Flask info logic while providing FastAPI-compatible responses.
"""

from fastapi import APIRouter

from models.info_models import InfoResponse

from ..dependencies import ConfigDep

router = APIRouter()


@router.get("", response_model=InfoResponse)
async def get_info(config: ConfigDep):
    """
    Get telescope general information.

    This endpoint reuses the existing Flask logic for telescope info reporting,
    including site location, operating frequencies, and antenna configuration.
    """
    t_c = config["telescope_config"]

    info_data = {
        "name": t_c["name"],
        "operating_frequency": t_c["frequency"],
        "L0_frequency": t_c["L0_frequency"],
        "baseband_frequency": t_c["baseband_frequency"],
        "sampling_frequency": t_c["sampling_frequency"],
        "bandwidth": t_c["bandwidth"],
        "num_antenna": t_c["num_antenna"],
        "location": {"lon": t_c["lon"], "lat": t_c["lat"], "alt": t_c["alt"]},
    }

    return InfoResponse(info=info_data)
