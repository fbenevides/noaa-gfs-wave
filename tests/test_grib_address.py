from datetime import UTC, datetime
from pathlib import Path

import pytest
from pydantic import ValidationError

from noaa_gfs_wave.grib_address import NOAA_NOMADS_BASE_URL, GribAddress


class TestGribAddress:
    def setup_method(self):
        self.address = GribAddress(
            reference_time=datetime(2026, 3, 9, tzinfo=UTC),
            cycle=12,
            forecast_hour=3,
        )

    def test_remote_relative_path(self):
        assert self.address.remote_relative_path() == (
            "gfs.20260309/12/wave/gridded/gfswave.t12z.global.0p25.f003.grib2"
        )

    def test_remote_url(self):
        assert self.address.remote_url() == (
            "https://nomads.ncep.noaa.gov/pub/data/nccf/com/gfs/prod/"
            "gfs.20260309/12/wave/gridded/gfswave.t12z.global.0p25.f003.grib2"
        )

    def test_local_path_str_cache_dir(self):
        p = self.address.local_path("/tmp/cache")
        assert isinstance(p, Path)
        assert p == Path("/tmp/cache/20260309_12_003.grib2")

    def test_local_path_path_cache_dir(self):
        p = self.address.local_path(Path("/tmp/cache"))
        assert p == Path("/tmp/cache/20260309_12_003.grib2")

    def test_cycle_two_digit_padding(self):
        addr = GribAddress(
            reference_time=datetime(2026, 3, 9, tzinfo=UTC), cycle=0, forecast_hour=0
        )
        assert "/gfs.20260309/00/wave" in addr.remote_url()

    def test_forecast_hour_three_digit_padding(self):
        addr = GribAddress(
            reference_time=datetime(2026, 3, 9, tzinfo=UTC), cycle=12, forecast_hour=120
        )
        assert "f120.grib2" in addr.remote_url()

    def test_local_path_zero_padded(self):
        addr = GribAddress(
            reference_time=datetime(2026, 3, 9, tzinfo=UTC), cycle=0, forecast_hour=0
        )
        assert addr.local_path("./cache").name == "20260309_00_000.grib2"

    def test_frozen_raises_on_assignment(self):
        with pytest.raises(ValidationError):
            self.address.reference_time = datetime(2025, 1, 1, tzinfo=UTC)

    def test_equality_same_fields(self):
        other = GribAddress(
            reference_time=datetime(2026, 3, 9, tzinfo=UTC),
            cycle=12,
            forecast_hour=3,
        )
        assert self.address == other

    def test_inequality_different_fields(self):
        other = GribAddress(
            reference_time=datetime(2026, 3, 9, tzinfo=UTC),
            cycle=6,
            forecast_hour=3,
        )
        assert self.address != other


class TestGribAddressBaseUrl:
    REF_TIME = datetime(2026, 3, 9, tzinfo=UTC)

    def test_default_base_url_is_noaa_nomads(self):
        address = GribAddress(reference_time=self.REF_TIME, cycle=12, forecast_hour=3)
        assert address.base_url == NOAA_NOMADS_BASE_URL
        assert address.remote_url().startswith(NOAA_NOMADS_BASE_URL)

    def test_custom_base_url_overrides_default(self):
        address = GribAddress(
            reference_time=self.REF_TIME,
            cycle=12,
            forecast_hour=3,
            base_url="https://mirror.example/gfs",
        )
        assert address.remote_url().startswith("https://mirror.example/gfs/")

    def test_base_url_trailing_slash_stripped(self):
        address = GribAddress(
            reference_time=self.REF_TIME,
            cycle=12,
            forecast_hour=3,
            base_url="https://mirror.example/gfs/",
        )
        url = address.remote_url()
        assert "https://mirror.example/gfs//" not in url
        assert url.startswith("https://mirror.example/gfs/")

    def test_base_url_immutable_on_frozen_model(self):
        address = GribAddress(reference_time=self.REF_TIME, cycle=12, forecast_hour=3)
        with pytest.raises(ValidationError):
            address.base_url = "https://other.example"
