"""GRIB2 remote URL and local path builders.

Public class and constant — no I/O, no network. Separated for testability.
"""

from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, ConfigDict, field_validator

NOAA_NOMADS_BASE_URL = "https://nomads.ncep.noaa.gov/pub/data/nccf/com/gfs/prod"


class GribAddress(BaseModel):
    """NOMADS address for a single GFS wave GRIB2 file — the
    (reference_time, cycle, forecast_hour) triple with derivation methods."""

    model_config = ConfigDict(frozen=True)

    reference_time: datetime
    cycle: int
    forecast_hour: int
    base_url: str = NOAA_NOMADS_BASE_URL

    @field_validator("base_url")
    @classmethod
    def strip_trailing_slash(cls, value: str) -> str:
        return value.rstrip("/")

    def remote_relative_path(self) -> str:
        """Return the NOMADS-relative path for a GFS wave GRIB2 file."""
        date_str = self.reference_time.strftime("%Y%m%d")
        return (
            f"gfs.{date_str}/{self.cycle:02d}/wave/gridded/"
            f"gfswave.t{self.cycle:02d}z.global.0p25.f{self.forecast_hour:03d}.grib2"
        )

    def remote_url(self) -> str:
        """Return the full URL for a GFS wave GRIB2 file."""
        return f"{self.base_url}/{self.remote_relative_path()}"

    def local_path(self, cache_dir: str | Path) -> Path:
        """Return the deterministic local cache path for a GFS wave GRIB2 file."""
        date_str = self.reference_time.strftime("%Y%m%d")
        filename = f"{date_str}_{self.cycle:02d}_{self.forecast_hour:03d}.grib2"
        return Path(cache_dir) / filename
