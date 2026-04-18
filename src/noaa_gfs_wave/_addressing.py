"""GRIB2 remote URL and local path builders.

Pure functions — no I/O, no network. Separated for testability.
"""

from datetime import datetime
from pathlib import Path

_NOAA_BASE_URL = "https://nomads.ncep.noaa.gov/pub/data/nccf/com/gfs/prod"


def remote_relative_path(reference_time: datetime, *, cycle: int, forecast_hour: int) -> str:
    """Return the NOMADS-relative path for a GFS wave GRIB2 file."""
    date_str = reference_time.strftime("%Y%m%d")
    return (
        f"gfs.{date_str}/{cycle:02d}/wave/gridded/"
        f"gfswave.t{cycle:02d}z.global.0p25.f{forecast_hour:03d}.grib2"
    )


def remote_url(reference_time: datetime, *, cycle: int, forecast_hour: int) -> str:
    """Return the full NOMADS URL for a GFS wave GRIB2 file."""
    rel = remote_relative_path(reference_time, cycle=cycle, forecast_hour=forecast_hour)
    return f"{_NOAA_BASE_URL}/{rel}"


def local_path(
    cache_dir: str | Path,
    reference_time: datetime,
    *,
    cycle: int,
    forecast_hour: int,
) -> Path:
    """Return the deterministic local cache path for a GFS wave GRIB2 file."""
    date_str = reference_time.strftime("%Y%m%d")
    filename = f"{date_str}_{cycle:02d}_{forecast_hour:03d}.grib2"
    return Path(cache_dir) / filename
