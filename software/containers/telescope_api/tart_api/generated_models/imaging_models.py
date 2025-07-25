# DO NOT EDIT! This file is auto-generated from JSON schemas.
# To make changes, edit the schema files and regenerate.

# generated by datamodel-codegen:
#   filename:  imaging.json
#   timestamp: 2025-07-19T12:33:22+00:00
#   version:   0.31.2

from __future__ import annotations
from typing import Annotated, Any
from pydantic import BaseModel, ConfigDict, Field, RootModel
from datetime import datetime


class Model(RootModel[Any]):
    root: Any


class VisibilityData(BaseModel):
    model_config = ConfigDict(
        extra="allow",
    )
    i: Annotated[int, Field(ge=0, le=23)]
    """
    First antenna index
    """
    j: Annotated[int, Field(ge=0, le=23)]
    """
    Second antenna index
    """


class VisibilityResponse(BaseModel):
    model_config = ConfigDict(
        extra="allow",
    )
    data: list[VisibilityData]


class AntennaPositionsResponseItem(RootModel[list[float]]):
    root: Annotated[list[float], Field(max_length=3, min_length=3)]
    """
    Antenna position in East-North-Up coordinate system [e,n,u]
    """


class AntennaPositionsResponse(RootModel[list[AntennaPositionsResponseItem]]):
    root: list[AntennaPositionsResponseItem]


class TimestampResponse(RootModel[datetime]):
    root: Annotated[datetime, Field(pattern=".*[Z]$|.*[+-]\\d{2}:\\d{2}$")]
    """
    UTC timestamp of latest visibilities in ISO format with timezone (must end with Z or +/-HH:MM)
    """


class EmptyResponse(BaseModel):
    pass
    model_config = ConfigDict(
        extra="forbid",
    )
