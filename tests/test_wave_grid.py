"""Tests for WaveGrid — uses synthetic numpy arrays instead of a real GRIB."""

from datetime import datetime
from unittest.mock import MagicMock

import numpy as np

from noaa_gfs_wave.models import WW3PointForecast
from noaa_gfs_wave.wave_grid import WaveGrid


def _make_dataset(lat_n: int = 49, lon_n: int = 61) -> MagicMock:
    """Build a fake xarray dataset shaped (lat_n, lon_n)."""
    rng = np.random.default_rng(42)
    shape = (lat_n, lon_n)
    part_shape = (3, lat_n, lon_n)

    lats = np.linspace(0.0, -12.0, lat_n)  # descending
    lons = np.linspace(320.0, 335.0, lon_n)

    def _da(arr):
        m = MagicMock()
        m.values = arr
        return m

    ds = MagicMock()
    ds.swh = _da(rng.random(shape).astype(np.float32))
    ds.perpw = _da(rng.random(shape).astype(np.float32) * 20)
    ds.dirpw = _da(rng.random(shape).astype(np.float32) * 360)
    ds.shww = _da(rng.random(shape).astype(np.float32))
    ds.mpww = _da(rng.random(shape).astype(np.float32) * 15)
    ds.wvdir = _da(rng.random(shape).astype(np.float32) * 360)
    ds.wvdirww = _da(rng.random(shape).astype(np.float32) * 360)
    ds.shts = _da(rng.random(part_shape).astype(np.float32))
    ds.mpts = _da(rng.random(part_shape).astype(np.float32) * 20)
    ds.swdir = _da(rng.random(part_shape).astype(np.float32) * 360)
    ds.ws = _da(rng.random(shape).astype(np.float32) * 15)
    ds.wdir = _da(rng.random(shape).astype(np.float32) * 360)
    ds.u = _da(rng.random(shape).astype(np.float32) * 10)
    ds.v = _da(rng.random(shape).astype(np.float32) * 10)

    ds.latitude = _da(lats)
    ds.longitude = _da(lons)

    ds.time = _da(np.datetime64("2026-03-09T06:00:00"))
    ds.step = _da(np.timedelta64(3, "h"))
    ds.valid_time = _da(np.datetime64("2026-03-09T09:00:00"))
    ds.surface = _da(np.float32(0.0))

    return ds


class TestWaveGridProperties:
    def setup_method(self):
        self.ds = _make_dataset()
        self.grid = WaveGrid(self.ds)

    def test_swh_shape(self):
        assert self.grid.swh.shape == (49, 61)

    def test_perpw_is_ndarray(self):
        assert isinstance(self.grid.perpw, np.ndarray)

    def test_dirpw_is_ndarray(self):
        assert isinstance(self.grid.dirpw, np.ndarray)

    def test_shww_is_ndarray(self):
        assert isinstance(self.grid.shww, np.ndarray)

    def test_shts_shape_three_partitions(self):
        assert self.grid.shts.shape == (3, 49, 61)

    def test_mpts_shape_three_partitions(self):
        assert self.grid.mpts.shape == (3, 49, 61)

    def test_swdir_shape_three_partitions(self):
        assert self.grid.swdir.shape == (3, 49, 61)

    def test_mpww_is_ndarray(self):
        assert isinstance(self.grid.mpww, np.ndarray)

    def test_wvdir_is_ndarray(self):
        assert isinstance(self.grid.wvdir, np.ndarray)

    def test_wvdirww_is_ndarray(self):
        assert isinstance(self.grid.wvdirww, np.ndarray)

    def test_ws_is_ndarray(self):
        assert isinstance(self.grid.ws, np.ndarray)

    def test_wdir_is_ndarray(self):
        assert isinstance(self.grid.wdir, np.ndarray)

    def test_u_is_ndarray(self):
        assert isinstance(self.grid.u, np.ndarray)

    def test_v_is_ndarray(self):
        assert isinstance(self.grid.v, np.ndarray)

    def test_latitudes_shape(self):
        assert self.grid.latitudes.shape == (49,)

    def test_longitudes_shape(self):
        assert self.grid.longitudes.shape == (61,)

    def test_dataset_property_is_same_object(self):
        assert self.grid.dataset is self.ds


class TestWaveGridAt:
    def setup_method(self):
        self.ds = _make_dataset()
        self.grid = WaveGrid(self.ds)

    def test_at_returns_ww3_point_forecast(self):
        point = self.grid.at(lat=-9.0, lon=324.8)
        assert isinstance(point, WW3PointForecast)

    def test_at_negative_lon_normalized(self):
        # -35.2 -> 324.8
        point_pos = self.grid.at(lat=-9.0, lon=324.8)
        point_neg = self.grid.at(lat=-9.0, lon=-35.2)
        assert (
            point_pos.combined.significant_height_meters
            == point_neg.combined.significant_height_meters
        )

    def test_at_lon_360_handled(self):
        # lon=360 should map to lon=0 (modulo 360)
        point = self.grid.at(lat=-9.0, lon=360.0)
        assert isinstance(point, WW3PointForecast)

    def test_indices_at_returns_tuple_of_ints(self):
        lat_idx, lon_idx = self.grid.indices_at(lat=-9.0, lon=324.8)
        assert isinstance(lat_idx, int)
        assert isinstance(lon_idx, int)

    def test_indices_at_within_bounds(self):
        lat_idx, lon_idx = self.grid.indices_at(lat=-9.0, lon=324.8)
        assert 0 <= lat_idx < 49
        assert 0 <= lon_idx < 61

    def test_at_land_point_returns_none_fields(self):
        # Force NaN in swh at (0, 0) to simulate land
        ds = _make_dataset()
        ds.swh.values[0, 0] = np.nan
        grid = WaveGrid(ds)
        # lat=0.0, lon=320.0 is the corner
        point = grid.at(lat=0.0, lon=320.0)
        assert point.combined.significant_height_meters is None


class TestWaveGridContextManager:
    def test_context_manager_closes_dataset(self):
        ds = _make_dataset()
        with WaveGrid(ds) as grid:
            assert isinstance(grid, WaveGrid)
        ds.close.assert_called_once()

    def test_close_calls_dataset_close(self):
        ds = _make_dataset()
        grid = WaveGrid(ds)
        grid.close()
        ds.close.assert_called_once()


class TestWaveGridForecastDate:
    def test_at_returns_forecast_date(self):
        ds = _make_dataset()
        grid = WaveGrid(ds)
        point = grid.at(lat=-9.0, lon=324.8)
        assert isinstance(point.forecast_date, datetime)
