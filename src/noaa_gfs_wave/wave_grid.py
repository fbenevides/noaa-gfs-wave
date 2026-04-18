"""WaveGrid — in-memory wrapper over a WaveWatch III GRIB dataset.

Typed accessors for every WW3 variable. `at()` extracts a point forecast
by nearest-neighbor grid match.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

import numpy as np

from noaa_gfs_wave._dataset import partition, scalar, time_str_or_none
from noaa_gfs_wave.exceptions import GribCorruptError
from noaa_gfs_wave.models import (
    CombinedSea,
    DominantSystem,
    SwellPartition,
    Wind10m,
    WindSea,
    WW3PointForecast,
    WW3PointMeta,
)

if TYPE_CHECKING:
    import xarray

    from noaa_gfs_wave.grib_file import NoaaGribFile


class WaveGrid:
    """In-memory wrapper over a WaveWatch III GRIB dataset.

    Typed accessors for every WW3 variable; `at()` extracts a point forecast
    by nearest-neighbor grid match. Construct via `NoaaGribFile.read()` or
    by passing a pre-loaded `xarray.Dataset` directly.
    """

    def __init__(self, dataset: xarray.Dataset, source: NoaaGribFile | None = None) -> None:
        self._ds = dataset
        self._source = source

    # -- Grid arrays ----------------------------------------------------------

    @property
    def swh(self) -> np.ndarray:
        """Significant wave height (m), shape (lat, lon)."""
        return np.asarray(self._ds.swh.values)

    @property
    def perpw(self) -> np.ndarray:
        """Dominant wave period (s), shape (lat, lon)."""
        return np.asarray(self._ds.perpw.values)

    @property
    def dirpw(self) -> np.ndarray:
        """Dominant wave direction (°), shape (lat, lon)."""
        return np.asarray(self._ds.dirpw.values)

    @property
    def shww(self) -> np.ndarray:
        """Wind sea height (m), shape (lat, lon)."""
        return np.asarray(self._ds.shww.values)

    @property
    def mpww(self) -> np.ndarray:
        """Wind sea period (s), shape (lat, lon)."""
        return np.asarray(self._ds.mpww.values)

    @property
    def wvdir(self) -> np.ndarray:
        """Mean wave direction combined (°), shape (lat, lon)."""
        return np.asarray(self._ds.wvdir.values)

    @property
    def wvdirww(self) -> np.ndarray:
        """Wind sea direction (°), shape (lat, lon)."""
        return np.asarray(self._ds.wvdirww.values)

    @property
    def shts(self) -> np.ndarray:
        """Swell partition heights (m), shape (3, lat, lon)."""
        return np.asarray(self._ds.shts.values)

    @property
    def mpts(self) -> np.ndarray:
        """Swell partition periods (s), shape (3, lat, lon)."""
        return np.asarray(self._ds.mpts.values)

    @property
    def swdir(self) -> np.ndarray:
        """Swell partition directions (°), shape (3, lat, lon)."""
        return np.asarray(self._ds.swdir.values)

    @property
    def ws(self) -> np.ndarray:
        """10 m wind speed (m/s), shape (lat, lon)."""
        return np.asarray(self._ds.ws.values)

    @property
    def wdir(self) -> np.ndarray:
        """10 m wind direction from (°), shape (lat, lon)."""
        return np.asarray(self._ds.wdir.values)

    @property
    def u(self) -> np.ndarray:
        """10 m eastward wind component (m/s), shape (lat, lon)."""
        return np.asarray(self._ds.u.values)

    @property
    def v(self) -> np.ndarray:
        """10 m northward wind component (m/s), shape (lat, lon)."""
        return np.asarray(self._ds.v.values)

    @property
    def latitudes(self) -> np.ndarray:
        """Latitude array, shape (lat,), descending 90 to -90."""
        return np.asarray(self._ds.latitude.values)

    @property
    def longitudes(self) -> np.ndarray:
        """Longitude array, shape (lon,), 0..360."""
        return np.asarray(self._ds.longitude.values)

    @property
    def dataset(self) -> Any:
        """The underlying xarray Dataset — escape hatch for advanced use."""
        return self._ds

    # -- Point extraction -----------------------------------------------------

    def indices_at(self, lat: float, lon: float) -> tuple[int, int]:
        """Return (lat_idx, lon_idx) for the nearest grid point to (lat, lon).

        `lon` is accepted in either -180..180 or 0..360. Values of 360 are
        normalized via modulo to avoid index overflow.
        """
        lon = lon % 360
        lat_idx = int(np.argmin(np.abs(self.latitudes - lat)))
        lon_idx = int(np.argmin(np.abs(self.longitudes - lon)))
        return lat_idx, lon_idx

    def at(self, lat: float, lon: float) -> WW3PointForecast:
        """Nearest-neighbor point forecast at (lat, lon).

        Returns a WW3PointForecast where numeric fields are None for land points
        (NaN values in the dataset). No error is raised for land or coastal points.
        """
        lat_idx, lon_idx = self.indices_at(lat, lon)
        point_ds = self._ds.isel(latitude=lat_idx, longitude=lon_idx)
        return self._build_forecast(point_ds)

    # -- Lifecycle ------------------------------------------------------------

    def close(self) -> None:
        """Close the underlying xarray dataset."""
        self._ds.close()

    def __enter__(self) -> WaveGrid:
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()

    # -- Private helpers ------------------------------------------------------

    def _build_forecast(self, point_ds: Any) -> WW3PointForecast:
        forecast_date = self._parse_valid_time(point_ds)
        meta = self._build_meta(point_ds)
        wind10m = self._build_wind10m(point_ds)
        combined = self._build_combined(point_ds)
        dominant = self._build_dominant(point_ds)
        wind_sea = self._build_wind_sea(point_ds)
        primary, secondary, tertiary = self._build_swells(point_ds)
        return WW3PointForecast(
            forecast_date=forecast_date,
            meta=meta,
            wind10m=wind10m,
            combined=combined,
            dominant=dominant,
            wind_sea=wind_sea,
            primary=primary,
            secondary=secondary,
            tertiary=tertiary,
        )

    def _parse_valid_time(self, point_ds: Any) -> datetime:
        raw = time_str_or_none("valid_time", point_ds)
        if raw is None:
            raise GribCorruptError("could not parse valid_time from GRIB dataset")
        try:
            ts = np.datetime64(raw)
            return datetime.fromtimestamp(ts.astype("int64") / 1e9, tz=UTC)
        except (TypeError, ValueError, AttributeError, OSError) as exc:
            raise GribCorruptError("could not parse valid_time from GRIB dataset") from exc

    def _build_meta(self, point_ds: Any) -> WW3PointMeta:
        filename = None
        if self._source is not None:
            filename = str(getattr(self._source, "local_path", None) or "")
        return WW3PointMeta(
            time_iso=time_str_or_none("time", point_ds),
            step_hours=scalar(point_ds, "step"),
            valid_time_iso=time_str_or_none("valid_time", point_ds),
            surface_level=scalar(point_ds, "surface"),
            latitude_degrees=scalar(point_ds, "latitude"),
            longitude_degrees=scalar(point_ds, "longitude"),
            filename=filename,
        )

    def _build_wind10m(self, point_ds: Any) -> Wind10m:
        return Wind10m(
            speed_meters_per_second=scalar(point_ds, "ws"),
            direction_degrees_from=scalar(point_ds, "wdir"),
            u_component_meters_per_second=scalar(point_ds, "u"),
            v_component_meters_per_second=scalar(point_ds, "v"),
        )

    def _build_combined(self, point_ds: Any) -> CombinedSea:
        return CombinedSea(
            significant_height_meters=scalar(point_ds, "swh"),
            mean_direction_degrees_from=scalar(point_ds, "wvdir"),
        )

    def _build_dominant(self, point_ds: Any) -> DominantSystem:
        return DominantSystem(
            period_seconds=scalar(point_ds, "perpw"),
            direction_degrees_from=scalar(point_ds, "dirpw"),
        )

    def _build_wind_sea(self, point_ds: Any) -> WindSea:
        return WindSea(
            significant_height_meters=scalar(point_ds, "shww"),
            mean_period_seconds=scalar(point_ds, "mpww"),
            direction_degrees_from=scalar(point_ds, "wvdirww"),
        )

    def _build_swells(self, point_ds: Any) -> tuple[SwellPartition, SwellPartition, SwellPartition]:
        return (
            SwellPartition(
                significant_height_meters=partition(point_ds, "shts", 0),
                mean_period_seconds=partition(point_ds, "mpts", 0),
                direction_degrees_from=partition(point_ds, "swdir", 0),
            ),
            SwellPartition(
                significant_height_meters=partition(point_ds, "shts", 1),
                mean_period_seconds=partition(point_ds, "mpts", 1),
                direction_degrees_from=partition(point_ds, "swdir", 1),
            ),
            SwellPartition(
                significant_height_meters=partition(point_ds, "shts", 2),
                mean_period_seconds=partition(point_ds, "mpts", 2),
                direction_degrees_from=partition(point_ds, "swdir", 2),
            ),
        )
