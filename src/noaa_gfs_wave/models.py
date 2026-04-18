"""Pydantic domain models for WaveWatch III forecast data.

All models are portable — zero Harper or external service imports.
Dependencies: stdlib (datetime) + pydantic only.
"""

from datetime import datetime

from pydantic import BaseModel


class Wind10m(BaseModel):
    """10-meter wind conditions at the forecast grid point."""

    speed_meters_per_second: float | None = None
    direction_degrees_from: float | None = None
    u_component_meters_per_second: float | None = None
    v_component_meters_per_second: float | None = None


class CombinedSea(BaseModel):
    """Combined (total) sea state — merges all wave systems."""

    significant_height_meters: float | None = None
    mean_direction_degrees_from: float | None = None


class DominantSystem(BaseModel):
    """The single wave system with the highest energy at this point."""

    period_seconds: float | None = None
    direction_degrees_from: float | None = None


class WindSea(BaseModel):
    """Locally generated waves driven by the wind at this point."""

    significant_height_meters: float | None = None
    mean_period_seconds: float | None = None
    direction_degrees_from: float | None = None


class SwellPartition(BaseModel):
    """One partitioned swell system (primary, secondary, or tertiary)."""

    significant_height_meters: float | None = None
    mean_period_seconds: float | None = None
    direction_degrees_from: float | None = None


class WW3PointMeta(BaseModel):
    """Metadata about the forecast point: timing, surface, and location."""

    time_iso: str | None = None
    step_hours: float | None = None
    valid_time_iso: str | None = None
    surface_level: float | None = None
    latitude_degrees: float | None = None
    longitude_degrees: float | None = None
    filename: str | None = None


class WW3PointForecast(BaseModel):
    """Complete WaveWatch III forecast for a single grid point."""

    forecast_date: datetime
    meta: WW3PointMeta
    wind10m: Wind10m
    combined: CombinedSea
    dominant: DominantSystem
    wind_sea: WindSea
    primary: SwellPartition
    secondary: SwellPartition
    tertiary: SwellPartition
