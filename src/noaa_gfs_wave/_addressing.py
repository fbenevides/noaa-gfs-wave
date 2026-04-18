"""GRIB2 URL and path builders — stub."""

from datetime import datetime
from pathlib import Path

_NOAA_BASE_URL = "https://nomads.ncep.noaa.gov/pub/data/nccf/com/gfs/prod"


def remote_relative_path(reference_time: datetime, *, cycle: int, forecast_hour: int) -> str:
    raise NotImplementedError


def remote_url(reference_time: datetime, *, cycle: int, forecast_hour: int) -> str:
    raise NotImplementedError


def local_path(cache_dir: str | Path, reference_time: datetime, *, cycle: int, forecast_hour: int) -> Path:
    raise NotImplementedError
