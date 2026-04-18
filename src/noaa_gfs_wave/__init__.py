"""noaa-gfs-wave — Read NOAA GFS WaveWatch III forecast data from NOMADS."""

from importlib.metadata import version

from noaa_gfs_wave._cycle import NOAA_CYCLES, latest_available_cycle
from noaa_gfs_wave.grib_file import NoaaGribFile

__version__ = version("noaa-gfs-wave")

__all__ = [
    "NOAA_CYCLES",
    "NoaaGribFile",
    "latest_available_cycle",
    "__version__",
]
