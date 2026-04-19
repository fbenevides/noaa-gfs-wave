"""NoaaGribFile — lazy download and cached GRIB2 access.

A single NOAA GFS wave GRIB2 file. Constructed either explicitly or via
`.latest()`. Download is lazy — triggered by `.read()`, `.download()`, or
`.open_dataset()` when the file is not cached.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from noaa_gfs_wave._cycle import latest_available_cycle
from noaa_gfs_wave._dataset import open_dataset
from noaa_gfs_wave._download import download_to
from noaa_gfs_wave.exceptions import GribCorruptError
from noaa_gfs_wave.grib_address import NOAA_NOMADS_BASE_URL, GribAddress
from noaa_gfs_wave.wave_grid import WaveGrid

_GRIB_PARSE_ERRORS = (EOFError, KeyError, ValueError, OSError)


class NoaaGribFile:
    """A single NOAA GFS wave GRIB2 file.

    No I/O on construction. Download is lazy — triggered by `.read()`,
    `.download()`, or `.open_dataset()` when the file is not cached.
    """

    def __init__(
        self,
        reference_time: datetime,
        cycle: int,
        forecast_hour: int,
        *,
        cache_dir: str | Path = "./noaa_cache",
        request_timeout: int = 30,
        base_url: str = NOAA_NOMADS_BASE_URL,
    ) -> None:
        self._address = GribAddress(
            reference_time=reference_time,
            cycle=cycle,
            forecast_hour=forecast_hour,
            base_url=base_url,
        )
        self._cache_dir = Path(cache_dir)
        self._request_timeout = request_timeout
        self._is_local_only = False
        self._local_path_override: Path | None = None

    @classmethod
    def latest(
        cls,
        forecast_hour: int,
        *,
        cache_dir: str | Path = "./noaa_cache",
        now: datetime | None = None,
        request_timeout: int = 30,
        base_url: str = NOAA_NOMADS_BASE_URL,
    ) -> NoaaGribFile:
        """Construct from the most recently published GFS wave cycle."""
        ref_time, cycle = latest_available_cycle(now)
        return cls(
            ref_time,
            cycle,
            forecast_hour,
            cache_dir=cache_dir,
            request_timeout=request_timeout,
            base_url=base_url,
        )

    @classmethod
    def from_local(
        cls,
        path: str | Path,
        *,
        reference_time: datetime | None = None,
        cycle: int | None = None,
        forecast_hour: int | None = None,
    ) -> NoaaGribFile:
        """Wrap an existing on-disk GRIB2 file — no network access."""
        path = Path(path)
        instance = cls(
            reference_time or datetime(1970, 1, 1, tzinfo=UTC),
            cycle or 0,
            forecast_hour or 0,
            cache_dir=path.parent,
        )
        instance._is_local_only = True
        instance._local_path_override = path
        return instance

    # -- Properties -----------------------------------------------------------

    @property
    def reference_time(self) -> datetime:
        return self._address.reference_time

    @property
    def cycle(self) -> int:
        return self._address.cycle

    @property
    def forecast_hour(self) -> int:
        return self._address.forecast_hour

    @property
    def remote_url(self) -> str:
        return self._address.remote_url()

    @property
    def local_path(self) -> Path:
        if self._is_local_only and self._local_path_override is not None:
            return self._local_path_override
        return self._address.local_path(self._cache_dir)

    # -- I/O methods ----------------------------------------------------------

    def exists(self) -> bool:
        """Filesystem check only — no network."""
        return self.local_path.exists()

    def download(self, *, force: bool = False) -> Path:
        """Download the GRIB2 file if not cached (or always when force=True).

        Raises:
            GribNotPublishedError: HTTP 404.
            GribDownloadError: any other HTTP error or network failure.
        """
        if not force and self.exists():
            return self.local_path
        download_to(self.remote_url, self.local_path, request_timeout=self._request_timeout)
        return self.local_path

    def read(self) -> WaveGrid:
        """Download if needed, load the full grid into memory, return a WaveGrid."""
        if not self._is_local_only:
            self.download()
        return self._load_wave_grid()

    def open_dataset(self) -> Any:
        """Download if needed and return the raw xarray.Dataset (lazy).

        The caller owns the handle and must close it.
        """
        if not self._is_local_only:
            self.download()
        return self._open_raw()

    # -- Private helpers ------------------------------------------------------

    def _load_wave_grid(self) -> WaveGrid:
        try:
            ds = open_dataset(str(self.local_path))
            ds.load()
            return WaveGrid(ds, source=self)
        except _GRIB_PARSE_ERRORS as exc:
            raise GribCorruptError(f"Failed to parse GRIB: {self.local_path}: {exc}") from exc

    def _open_raw(self) -> Any:
        try:
            return open_dataset(str(self.local_path))
        except _GRIB_PARSE_ERRORS as exc:
            raise GribCorruptError(f"Failed to open GRIB: {self.local_path}: {exc}") from exc
