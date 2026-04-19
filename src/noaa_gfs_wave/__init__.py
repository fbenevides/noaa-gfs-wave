"""noaa-gfs-wave — Read NOAA GFS WaveWatch III forecast data from NOMADS."""

from importlib.metadata import version

from noaa_gfs_wave._cycle import NOAA_CYCLES, latest_available_cycle
from noaa_gfs_wave.exceptions import (
    GribCorruptError,
    GribDownloadError,
    GribNotPublishedError,
    NoaaGfsWaveError,
)
from noaa_gfs_wave.grib_address import NOAA_NOMADS_BASE_URL, GribAddress
from noaa_gfs_wave.grib_file import NoaaGribFile
from noaa_gfs_wave.models import (
    CombinedSea,
    DominantSystem,
    SwellPartition,
    Wind10m,
    WindSea,
    WW3PointForecast,
    WW3PointMeta,
)
from noaa_gfs_wave.wave_grid import WaveGrid

__version__ = version("noaa-gfs-wave")

__all__ = [
    # Core classes
    "GribAddress",
    "NoaaGribFile",
    "WaveGrid",
    # Pydantic models
    "WW3PointForecast",
    "WW3PointMeta",
    "Wind10m",
    "CombinedSea",
    "DominantSystem",
    "WindSea",
    "SwellPartition",
    # Cycle utilities
    "latest_available_cycle",
    "NOAA_CYCLES",
    # Constants
    "NOAA_NOMADS_BASE_URL",
    # Exceptions
    "NoaaGfsWaveError",
    "GribDownloadError",
    "GribNotPublishedError",
    "GribCorruptError",
    # Package metadata
    "__version__",
]
