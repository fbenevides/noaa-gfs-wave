"""NoaaGribFile — stub."""

from datetime import datetime
from pathlib import Path
from typing import Any

from noaa_gfs_wave._dataset import open_dataset


class NoaaGribFile:
    def __init__(
        self,
        reference_time: datetime,
        cycle: int,
        forecast_hour: int,
        *,
        cache_dir: str | Path = "./noaa_cache",
        request_timeout: int = 30,
    ) -> None:
        raise NotImplementedError
