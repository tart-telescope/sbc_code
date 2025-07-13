"""
Acquisition router for TART telescope API.

This module provides data acquisition endpoints that reuse the existing
Flask acquisition logic while providing FastAPI-compatible responses.
"""

from fastapi import APIRouter

from generated_models.acquisition_models import (
    SampleExponentResponse,
    SaveFlagResponse,
)

from ..dependencies import AuthDep, ConfigDep

router = APIRouter()


@router.put("/raw/save/{flag}", response_model=SaveFlagResponse)
async def set_raw_save_flag(flag: int, config: ConfigDep, _: AuthDep):
    """
    Set save flag for raw data acquisition.

    This endpoint reuses the existing Flask logic for raw data save configuration.
    Requires JWT authentication.
    """
    config["raw"]["save"] = flag
    return SaveFlagResponse(save=config["raw"]["save"])


@router.put("/vis/save/{flag}", response_model=SaveFlagResponse)
async def set_vis_save_flag(flag: int, config: ConfigDep, _: AuthDep):
    """
    Set save flag for visibility data acquisition.

    This endpoint reuses the existing Flask logic for visibility data save configuration.
    Requires JWT authentication.
    """
    config["vis"]["save"] = flag
    return SaveFlagResponse(save=config["vis"]["save"])


@router.put("/raw/num_samples_exp/{exp}", response_model=SampleExponentResponse)
async def set_raw_num_samples_exp(exp: int, config: ConfigDep, _: AuthDep):
    """
    Set exponent for number of samples for raw data acquisition (2**exp).

    This endpoint reuses the existing Flask logic for raw data sample configuration.
    Requires JWT authentication.
    """
    if 16 <= exp <= 24:
        config["raw"]["N_samples_exp"] = exp
    return SampleExponentResponse(N_samples_exp=config["raw"]["N_samples_exp"])


@router.put("/vis/num_samples_exp/{exp}", response_model=SampleExponentResponse)
async def set_vis_num_samples_exp(exp: int, config: ConfigDep, _: AuthDep):
    """
    Set exponent for number of samples for visibility data acquisition (2**exp).

    This endpoint reuses the existing Flask logic for visibility data sample configuration.
    Requires JWT authentication.
    """
    if 16 <= exp <= 24:
        config["vis"]["N_samples_exp"] = exp
    return SampleExponentResponse(N_samples_exp=config["vis"]["N_samples_exp"])


@router.get("/raw/save", response_model=SaveFlagResponse)
async def get_raw_save_flag(config: ConfigDep):
    """
    Get save flag for raw data acquisition.

    This endpoint reuses the existing Flask logic for raw data save status.
    """
    return SaveFlagResponse(save=config["raw"]["save"])


@router.get("/vis/save", response_model=SaveFlagResponse)
async def get_vis_save_flag(config: ConfigDep):
    """
    Get save flag for visibility data acquisition.

    This endpoint reuses the existing Flask logic for visibility data save status.
    """
    return SaveFlagResponse(save=config["vis"]["save"])


@router.get("/raw/num_samples_exp", response_model=SampleExponentResponse)
async def get_raw_num_samples_exp(config: ConfigDep):
    """
    Get exponent for number of samples for raw data acquisition (2**exp).

    This endpoint reuses the existing Flask logic for raw data sample configuration.
    """
    return SampleExponentResponse(N_samples_exp=config["raw"]["N_samples_exp"])


@router.get("/vis/num_samples_exp", response_model=SampleExponentResponse)
async def get_vis_num_samples_exp(config: ConfigDep):
    """
    Get exponent for number of samples for visibility data acquisition (2**exp).

    This endpoint reuses the existing Flask logic for visibility data sample configuration.
    """
    return SampleExponentResponse(N_samples_exp=config["vis"]["N_samples_exp"])
