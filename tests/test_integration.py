"""Integration test against the real GRIB fixture.

tests/fixtures/sample.grib2 is a 55 KB crop of the full 721x1440 grid
covering lat -12..0, lon 320..335 (around Alagoas, Brazil).
Reference time: 2026-03-09 06z, forecast hour 3.
"""

from datetime import UTC, datetime
from pathlib import Path

import pytest

from noaa_gfs_wave import NoaaGribFile
from noaa_gfs_wave.models import WW3PointForecast

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "sample.grib2"
REF_TIME = datetime(2026, 3, 9, 0, 0, 0, tzinfo=UTC)

# Ocean point confirmed inside the fixture region (lat -12..0, lon 320..335)
# Using lat=0.0, lon=321.0 which is a known ocean point with valid SWH data
LAT = 0.0
LON = 321.0


@pytest.fixture
def local_grib():
    """A NoaaGribFile wrapping the fixture."""
    assert FIXTURE_PATH.exists(), f"Fixture missing: {FIXTURE_PATH}"
    return NoaaGribFile.from_local(FIXTURE_PATH)


class TestIntegrationFromLocal:
    def test_exists_returns_true(self, local_grib: NoaaGribFile):
        assert local_grib.exists()

    def test_read_returns_wave_grid(self, local_grib: NoaaGribFile):
        from noaa_gfs_wave.wave_grid import WaveGrid

        grid = local_grib.read()
        assert isinstance(grid, WaveGrid)

    def test_at_returns_ww3_point_forecast(self, local_grib: NoaaGribFile):
        grid = local_grib.read()
        point = grid.at(lat=LAT, lon=LON)
        assert isinstance(point, WW3PointForecast)

    def test_at_has_significant_wave_height(self, local_grib: NoaaGribFile):
        grid = local_grib.read()
        point = grid.at(lat=LAT, lon=LON)
        # This is an ocean point — swh should be a positive float
        assert point.combined.significant_height_meters is not None
        assert point.combined.significant_height_meters > 0

    def test_at_has_dominant_period(self, local_grib: NoaaGribFile):
        grid = local_grib.read()
        point = grid.at(lat=LAT, lon=LON)
        assert point.dominant.period_seconds is not None
        assert point.dominant.period_seconds > 0

    def test_grid_shape_matches_fixture(self, local_grib: NoaaGribFile):
        grid = local_grib.read()
        # Fixture: lat -12..0 (49 pts), lon 320..335 (61 pts)
        assert grid.swh.shape == (49, 61)

    def test_indices_at_within_fixture_bounds(self, local_grib: NoaaGribFile):
        grid = local_grib.read()
        lat_idx, lon_idx = grid.indices_at(lat=LAT, lon=LON)
        assert 0 <= lat_idx < 49
        assert 0 <= lon_idx < 61

    def test_forecast_date_is_datetime(self, local_grib: NoaaGribFile):
        grid = local_grib.read()
        point = grid.at(lat=LAT, lon=LON)
        assert isinstance(point.forecast_date, datetime)

    def test_context_manager_usage(self):
        grib = NoaaGribFile.from_local(FIXTURE_PATH)
        with grib.read() as grid:
            point = grid.at(lat=LAT, lon=LON)
        assert isinstance(point, WW3PointForecast)
