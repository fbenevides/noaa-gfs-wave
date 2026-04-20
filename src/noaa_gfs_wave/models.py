"""Pydantic domain models for WaveWatch III forecast data.

All models are portable — zero Harper or external service imports.
Dependencies: stdlib (datetime) + pydantic only.
"""

import math
from datetime import datetime

from pydantic import BaseModel, computed_field

_MPS_TO_KNOTS = 3600 / 1852
_WAVE_POWER_COEFF_KW_PER_M = 1025 * 9.81**2 / (64 * math.pi * 1000)


class Wind10m(BaseModel):
    """10-meter wind conditions at the forecast grid point."""

    speed_meters_per_second: float | None = None
    direction_degrees_from: float | None = None
    u_component_meters_per_second: float | None = None
    v_component_meters_per_second: float | None = None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def speed_knots(self) -> float | None:
        if self.speed_meters_per_second is None:
            return None
        return self.speed_meters_per_second * _MPS_TO_KNOTS


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

    def is_land(self) -> bool:
        return self.combined.significant_height_meters is None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def power_kilowatts_per_meter(self) -> float | None:
        if self.is_land():
            return None
        parts = (self.wind_sea, self.primary, self.secondary, self.tertiary)
        contribs = [
            _WAVE_POWER_COEFF_KW_PER_M * p.significant_height_meters**2 * p.mean_period_seconds
            for p in parts
            if p.significant_height_meters is not None and p.mean_period_seconds is not None
        ]
        return sum(contribs) if contribs else None
