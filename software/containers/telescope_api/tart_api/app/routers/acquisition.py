"""
Acquisition router for TART telescope API.

This module provides data acquisition endpoints that reuse the existing
Flask acquisition logic while providing FastAPI-compatible responses.
"""

from typing import Annotated

from fastapi import APIRouter, Depends

from database import AsyncDatabase, get_database
from generated_models.acquisition_models import (
    SampleExponentResponse,
    SaveFlagResponse,
    SyncResponse,
    SyncAcquireAtSecondsResponse,
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
    # For managed dict, we need to update nested dict properly
    raw_config = config["raw"]
    raw_config["save"] = flag
    config["raw"] = raw_config
    return SaveFlagResponse(save=config["raw"]["save"])


@router.put("/vis/save/{flag}", response_model=SaveFlagResponse)
async def set_vis_save_flag(flag: int, config: ConfigDep, _: AuthDep):
    """
    Set save flag for visibility data acquisition.

    This endpoint reuses the existing Flask logic for visibility data save configuration.
    Requires JWT authentication.
    """
    # For managed dict, we need to update nested dict properly
    vis_config = config["vis"]
    vis_config["save"] = flag
    config["vis"] = vis_config
    return SaveFlagResponse(save=config["vis"]["save"])


@router.put("/raw/num_samples_exp/{exp}", response_model=SampleExponentResponse)
async def set_raw_num_samples_exp(exp: int, config: ConfigDep, _: AuthDep):
    """
    Set exponent for number of samples for raw data acquisition (2**exp).

    This endpoint reuses the existing Flask logic for raw data sample configuration.
    Requires JWT authentication.
    """
    if 16 <= exp <= 24:
        # For managed dict, we need to update nested dict properly
        raw_config = config["raw"]
        raw_config["N_samples_exp"] = exp
        config["raw"] = raw_config
    return SampleExponentResponse(N_samples_exp=config["raw"]["N_samples_exp"])


@router.put("/vis/num_samples_exp/{exp}", response_model=SampleExponentResponse)
async def set_vis_num_samples_exp(exp: int, config: ConfigDep, _: AuthDep):
    """
    Set exponent for number of samples for visibility data acquisition (2**exp).

    This endpoint reuses the existing Flask logic for visibility data sample configuration.
    Requires JWT authentication.
    """
    if 16 <= exp <= 24:
        # For managed dict, we need to update nested dict properly
        vis_config = config["vis"]
        vis_config["N_samples_exp"] = exp
        config["vis"] = vis_config
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


@router.put("/raw/sync/{flag}", response_model=SyncResponse)
async def set_raw_sync(
    flag: int, config: ConfigDep, _: AuthDep, db: Annotated[AsyncDatabase, Depends(get_database)]
):
    """
    Enable or disable synchronized acquisition start times.

    When enabled, raw acquisition will wait until the next allowed
    second-of-the-minute (as configured in sync_acquire_at_seconds)
    before starting. When disabled, acquisition starts immediately.
    Requires JWT authentication.
    """
    raw_config = config["raw"]
    raw_config["sync"] = flag
    config["raw"] = raw_config
    await db.set_setting("raw.sync", flag)
    return SyncResponse(sync=config["raw"]["sync"])


@router.get("/raw/sync", response_model=SyncResponse)
async def get_raw_sync(config: ConfigDep):
    """
    Get the synchronized acquisition flag for raw data acquisition.
    """
    return SyncResponse(sync=config["raw"].get("sync", 0))


@router.put("/raw/sync_acquire_at_seconds", response_model=SyncAcquireAtSecondsResponse)
async def set_raw_sync_acquire_at_seconds(
    seconds: list[int], config: ConfigDep, _: AuthDep, db: Annotated[AsyncDatabase, Depends(get_database)]
):
    """
    Set the allowed seconds-of-the-minute at which raw acquisition may start.

    Provide a list of second values (0-59). When sync is enabled and the
    system is ready to acquire, it will wait until the clock hits one of
    these seconds before starting.
    Example: [0, 10, 20, 30, 40, 50] means acquisition can begin at
    :00, :10, :20, :30, :40, or :50 of any minute.
    Requires JWT authentication.
    """
    # Validate all values are in range 0-59
    validated = sorted(set(s for s in seconds if 0 <= s <= 59))
    if validated:
        raw_config = config["raw"]
        raw_config["sync_acquire_at_seconds"] = validated
        config["raw"] = raw_config
        await db.set_setting("raw.sync_acquire_at_seconds", validated)
    return SyncAcquireAtSecondsResponse(sync_acquire_at_seconds=config["raw"].get("sync_acquire_at_seconds", [0, 10, 20, 30, 40, 50]))


@router.get("/raw/sync_acquire_at_seconds", response_model=SyncAcquireAtSecondsResponse)
async def get_raw_sync_acquire_at_seconds(config: ConfigDep):
    """
    Get the allowed seconds-of-the-minute at which raw acquisition may start.
    """
    return SyncAcquireAtSecondsResponse(sync_acquire_at_seconds=config["raw"].get("sync_acquire_at_seconds", [0, 10, 20, 30, 40, 50]))
