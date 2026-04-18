from datetime import UTC, datetime
from pathlib import Path

from noaa_gfs_wave._addressing import local_path, remote_relative_path, remote_url


class TestAddressing:
    def setup_method(self):
        self.ref = datetime(2026, 3, 9, 0, 0, 0, tzinfo=UTC)

    def test_remote_url_format(self):
        url = remote_url(self.ref, cycle=6, forecast_hour=3)
        assert url == (
            "https://nomads.ncep.noaa.gov/pub/data/nccf/com/gfs/prod/"
            "gfs.20260309/06/wave/gridded/gfswave.t06z.global.0p25.f003.grib2"
        )

    def test_remote_url_pads_cycle_two_digits(self):
        url = remote_url(self.ref, cycle=0, forecast_hour=0)
        assert "/gfs.20260309/00/wave" in url

    def test_remote_url_pads_forecast_hour_three_digits(self):
        url = remote_url(self.ref, cycle=12, forecast_hour=120)
        assert "f120.grib2" in url

    def test_remote_relative_path(self):
        path = remote_relative_path(self.ref, cycle=6, forecast_hour=3)
        assert path == "gfs.20260309/06/wave/gridded/gfswave.t06z.global.0p25.f003.grib2"

    def test_local_path_str_cache_dir(self):
        p = local_path("./cache", self.ref, cycle=6, forecast_hour=3)
        assert isinstance(p, Path)
        assert str(p) == "cache/20260309_06_003.grib2"

    def test_local_path_path_cache_dir(self):
        p = local_path(Path("/tmp/grib"), self.ref, cycle=6, forecast_hour=3)
        assert p == Path("/tmp/grib/20260309_06_003.grib2")

    def test_local_path_zero_padded(self):
        p = local_path("./cache", self.ref, cycle=0, forecast_hour=0)
        assert p.name == "20260309_00_000.grib2"

    def test_local_path_includes_date(self):
        p = local_path("./cache", self.ref, cycle=18, forecast_hour=240)
        assert "20260309" in p.name
        assert "18" in p.name
        assert "240" in p.name
