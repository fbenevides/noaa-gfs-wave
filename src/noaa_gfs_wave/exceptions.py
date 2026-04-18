"""Exception hierarchy for noaa-gfs-wave."""


class NoaaGfsWaveError(Exception):
    """Base exception for all noaa-gfs-wave errors."""


class GribDownloadError(NoaaGfsWaveError):
    """HTTP 4xx/5xx or network failure during GRIB download."""


class GribNotPublishedError(GribDownloadError):
    """HTTP 404 — cycle not yet published on NOMADS."""


class GribCorruptError(NoaaGfsWaveError):
    """cfgrib / xarray failed to parse the GRIB file."""
