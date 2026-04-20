from noaa_gfs_wave.models import (
    CombinedSea,
    DominantSystem,
    SwellPartition,
    Wind10m,
    WindSea,
    WW3PointForecast,
    WW3PointMeta,
)


class TestWind10m:
    def test_all_fields_none_by_default(self):
        w = Wind10m()
        assert w.speed_meters_per_second is None
        assert w.direction_degrees_from is None
        assert w.u_component_meters_per_second is None
        assert w.v_component_meters_per_second is None

    def test_accepts_float_values(self):
        w = Wind10m(speed_meters_per_second=5.2, direction_degrees_from=180.0)
        assert w.speed_meters_per_second == 5.2

    def test_speed_knots_is_none_when_speed_meters_per_second_is_none(self):
        w = Wind10m()
        assert w.speed_knots is None

    def test_speed_knots_converts_from_meters_per_second(self):
        import pytest

        w = Wind10m(speed_meters_per_second=10.0)
        assert w.speed_knots == pytest.approx(10.0 * 3600 / 1852)


class TestCombinedSea:
    def test_all_fields_optional(self):
        cs = CombinedSea()
        assert cs.significant_height_meters is None
        assert cs.mean_direction_degrees_from is None

    def test_accepts_values(self):
        cs = CombinedSea(significant_height_meters=1.5, mean_direction_degrees_from=90.0)
        assert cs.significant_height_meters == 1.5


class TestDominantSystem:
    def test_all_fields_optional(self):
        ds = DominantSystem()
        assert ds.period_seconds is None
        assert ds.direction_degrees_from is None


class TestWindSea:
    def test_all_fields_optional(self):
        ws = WindSea()
        assert ws.significant_height_meters is None
        assert ws.mean_period_seconds is None
        assert ws.direction_degrees_from is None


class TestSwellPartition:
    def test_all_fields_optional(self):
        sp = SwellPartition()
        assert sp.significant_height_meters is None
        assert sp.mean_period_seconds is None
        assert sp.direction_degrees_from is None


class TestWW3PointMeta:
    def test_filename_is_optional(self):
        meta = WW3PointMeta()
        assert meta.filename is None

    def test_accepts_filename(self):
        meta = WW3PointMeta(filename="20260309_06_003.grib2")
        assert meta.filename == "20260309_06_003.grib2"

    def test_all_fields_optional(self):
        meta = WW3PointMeta()
        assert meta.time_iso is None
        assert meta.step_hours is None
        assert meta.valid_time_iso is None
        assert meta.surface_level is None
        assert meta.latitude_degrees is None
        assert meta.longitude_degrees is None


class TestWW3PointForecast:
    def _make_forecast(self):
        from datetime import UTC, datetime

        return WW3PointForecast(
            forecast_date=datetime(2026, 3, 9, 9, 0, tzinfo=UTC),
            meta=WW3PointMeta(),
            wind10m=Wind10m(),
            combined=CombinedSea(),
            dominant=DominantSystem(),
            wind_sea=WindSea(),
            primary=SwellPartition(),
            secondary=SwellPartition(),
            tertiary=SwellPartition(),
        )

    def test_constructs_with_all_none_submodels(self):
        forecast = self._make_forecast()
        assert forecast.combined.significant_height_meters is None
        assert forecast.wind10m.speed_meters_per_second is None

    def test_has_forecast_date(self):
        from datetime import UTC, datetime

        forecast = self._make_forecast()
        assert forecast.forecast_date == datetime(2026, 3, 9, 9, 0, tzinfo=UTC)


class TestWW3PointForecastIsLand:
    def _make_forecast(self, combined_height: float | None):
        from datetime import UTC, datetime

        return WW3PointForecast(
            forecast_date=datetime(2026, 3, 9, 9, 0, tzinfo=UTC),
            meta=WW3PointMeta(),
            wind10m=Wind10m(),
            combined=CombinedSea(significant_height_meters=combined_height),
            dominant=DominantSystem(),
            wind_sea=WindSea(),
            primary=SwellPartition(),
            secondary=SwellPartition(),
            tertiary=SwellPartition(),
        )

    def test_is_land_returns_true_when_combined_height_is_none(self):
        forecast = self._make_forecast(combined_height=None)
        assert forecast.is_land() is True

    def test_is_land_returns_false_for_ocean_point(self):
        forecast = self._make_forecast(combined_height=1.5)
        assert forecast.is_land() is False


class TestNoHarperImports:
    def test_models_module_has_no_harper_imports(self):
        import inspect

        import noaa_gfs_wave.models as m

        src = inspect.getsource(m)
        assert "common.harper" not in src
        assert "common.external" not in src
        assert "from harper" not in src
