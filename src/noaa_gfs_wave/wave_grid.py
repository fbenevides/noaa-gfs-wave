"""WaveGrid — stub."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

from noaa_gfs_wave.models import WW3PointForecast

if TYPE_CHECKING:
    pass


class WaveGrid:
    def __init__(self, dataset: Any, source: Any = None) -> None:
        raise NotImplementedError
