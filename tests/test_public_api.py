"""Assert that the public API surface (__all__) is stable and fully importable."""

import noaa_gfs_wave

EXPECTED_PUBLIC_NAMES = {
    "GribAddress",
    "NoaaGribFile",
    "WaveGrid",
    "WW3PointForecast",
    "WW3PointMeta",
    "Wind10m",
    "CombinedSea",
    "DominantSystem",
    "WindSea",
    "SwellPartition",
    "latest_available_cycle",
    "NOAA_CYCLES",
    "NOAA_NOMADS_BASE_URL",
    "__version__",
}

EXPECTED_EXCEPTIONS = {
    "NoaaGfsWaveError",
    "GribDownloadError",
    "GribNotPublishedError",
    "GribCorruptError",
}


class TestPublicApiSurface:
    def test_all_contains_expected_names(self):
        assert set(noaa_gfs_wave.__all__) == EXPECTED_PUBLIC_NAMES | EXPECTED_EXCEPTIONS

    def test_all_names_are_importable(self):
        for name in EXPECTED_PUBLIC_NAMES | EXPECTED_EXCEPTIONS:
            assert hasattr(noaa_gfs_wave, name), f"Missing from noaa_gfs_wave: {name}"

    def test_version_is_string(self):
        assert isinstance(noaa_gfs_wave.__version__, str)
        assert noaa_gfs_wave.__version__ == "0.1.0"

    def test_noaa_cycles_constant(self):
        assert noaa_gfs_wave.NOAA_CYCLES == [0, 6, 12, 18]

    def test_exception_hierarchy(self):
        from noaa_gfs_wave.exceptions import (
            GribCorruptError,
            GribDownloadError,
            GribNotPublishedError,
            NoaaGfsWaveError,
        )

        assert issubclass(GribDownloadError, NoaaGfsWaveError)
        assert issubclass(GribNotPublishedError, GribDownloadError)
        assert issubclass(GribCorruptError, NoaaGfsWaveError)

    def test_no_harper_imports_in_public_modules(self):
        import inspect

        import noaa_gfs_wave.grib_file as gf
        import noaa_gfs_wave.models as m
        import noaa_gfs_wave.wave_grid as wg

        for mod in (gf, wg, m):
            src = inspect.getsource(mod)
            assert "common.harper" not in src, f"{mod.__name__} imports from harper"
            assert "common.external" not in src, f"{mod.__name__} imports from harper external"
