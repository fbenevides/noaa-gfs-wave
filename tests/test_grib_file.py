"""Tests for NoaaGribFile — mocked network and filesystem."""

from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import responses as responses_lib

from noaa_gfs_wave import NoaaGribFile
from noaa_gfs_wave.exceptions import GribCorruptError, GribDownloadError, GribNotPublishedError
from noaa_gfs_wave.wave_grid import WaveGrid

REF_TIME = datetime(2026, 3, 9, 0, 0, 0, tzinfo=UTC)
EXPECTED_URL = (
    "https://nomads.ncep.noaa.gov/pub/data/nccf/com/gfs/prod/"
    "gfs.20260309/06/wave/gridded/gfswave.t06z.global.0p25.f003.grib2"
)


class TestNoaaGribFileConstruction:
    def test_properties_set_on_construction(self, tmp_path: Path):
        grib = NoaaGribFile(REF_TIME, 6, 3, cache_dir=tmp_path)
        assert grib.reference_time == REF_TIME
        assert grib.cycle == 6
        assert grib.forecast_hour == 3

    def test_remote_url_property(self, tmp_path: Path):
        grib = NoaaGribFile(REF_TIME, 6, 3, cache_dir=tmp_path)
        assert grib.remote_url == EXPECTED_URL

    def test_local_path_property(self, tmp_path: Path):
        grib = NoaaGribFile(REF_TIME, 6, 3, cache_dir=tmp_path)
        assert grib.local_path == tmp_path / "20260309_06_003.grib2"

    def test_no_io_on_construction(self, tmp_path: Path):
        # Construction must not trigger any network or filesystem I/O
        grib = NoaaGribFile(REF_TIME, 6, 3, cache_dir=tmp_path)
        assert not grib.local_path.exists()

    def test_string_cache_dir_accepted(self, tmp_path: Path):
        grib = NoaaGribFile(REF_TIME, 6, 3, cache_dir=str(tmp_path))
        assert isinstance(grib.local_path, Path)


class TestNoaaGribFileExists:
    def test_exists_false_when_file_missing(self, tmp_path: Path):
        grib = NoaaGribFile(REF_TIME, 6, 3, cache_dir=tmp_path)
        assert not grib.exists()

    def test_exists_true_when_file_present(self, tmp_path: Path):
        grib = NoaaGribFile(REF_TIME, 6, 3, cache_dir=tmp_path)
        grib.local_path.parent.mkdir(parents=True, exist_ok=True)
        grib.local_path.write_bytes(b"GRIB")
        assert grib.exists()


class TestNoaaGribFileDownload:
    @responses_lib.activate
    def test_download_writes_file(self, tmp_path: Path):
        responses_lib.add(responses_lib.GET, EXPECTED_URL, body=b"GRIB_DATA", status=200)
        grib = NoaaGribFile(REF_TIME, 6, 3, cache_dir=tmp_path)
        path = grib.download()
        assert path == grib.local_path
        assert path.read_bytes() == b"GRIB_DATA"

    @responses_lib.activate
    def test_download_skips_if_cached(self, tmp_path: Path):
        grib = NoaaGribFile(REF_TIME, 6, 3, cache_dir=tmp_path)
        grib.local_path.parent.mkdir(parents=True, exist_ok=True)
        grib.local_path.write_bytes(b"CACHED")
        # No HTTP mock — would fail if download actually fired
        path = grib.download()
        assert path.read_bytes() == b"CACHED"

    @responses_lib.activate
    def test_download_force_redownloads(self, tmp_path: Path):
        responses_lib.add(responses_lib.GET, EXPECTED_URL, body=b"NEW_DATA", status=200)
        grib = NoaaGribFile(REF_TIME, 6, 3, cache_dir=tmp_path)
        grib.local_path.parent.mkdir(parents=True, exist_ok=True)
        grib.local_path.write_bytes(b"OLD_DATA")
        grib.download(force=True)
        assert grib.local_path.read_bytes() == b"NEW_DATA"

    @responses_lib.activate
    def test_download_raises_not_published_on_404(self, tmp_path: Path):
        responses_lib.add(responses_lib.GET, EXPECTED_URL, status=404)
        grib = NoaaGribFile(REF_TIME, 6, 3, cache_dir=tmp_path)
        with pytest.raises(GribNotPublishedError):
            grib.download()

    @responses_lib.activate
    def test_download_raises_download_error_on_500(self, tmp_path: Path):
        responses_lib.add(responses_lib.GET, EXPECTED_URL, status=500)
        grib = NoaaGribFile(REF_TIME, 6, 3, cache_dir=tmp_path)
        with pytest.raises(GribDownloadError):
            grib.download()


class TestNoaaGribFileRead:
    @responses_lib.activate
    def test_read_returns_wave_grid(self, tmp_path: Path):
        responses_lib.add(responses_lib.GET, EXPECTED_URL, body=b"GRIB_DATA", status=200)
        grib = NoaaGribFile(REF_TIME, 6, 3, cache_dir=tmp_path)
        with patch("noaa_gfs_wave.grib_file.open_dataset") as mock_open:
            mock_ds = MagicMock()
            mock_open.return_value = mock_ds
            result = grib.read()
        assert isinstance(result, WaveGrid)

    @responses_lib.activate
    def test_read_raises_corrupt_on_eof_error(self, tmp_path: Path):
        responses_lib.add(responses_lib.GET, EXPECTED_URL, body=b"BAD_DATA", status=200)
        grib = NoaaGribFile(REF_TIME, 6, 3, cache_dir=tmp_path)
        with patch("noaa_gfs_wave.grib_file.open_dataset", side_effect=EOFError("corrupt")):
            with pytest.raises(GribCorruptError):
                grib.read()

    @responses_lib.activate
    def test_read_raises_corrupt_on_key_error(self, tmp_path: Path):
        responses_lib.add(responses_lib.GET, EXPECTED_URL, body=b"BAD_DATA", status=200)
        grib = NoaaGribFile(REF_TIME, 6, 3, cache_dir=tmp_path)
        with patch("noaa_gfs_wave.grib_file.open_dataset", side_effect=KeyError("swh")):
            with pytest.raises(GribCorruptError):
                grib.read()


class TestNoaaGribFileOpenDataset:
    @responses_lib.activate
    def test_open_dataset_returns_dataset(self, tmp_path: Path):
        responses_lib.add(responses_lib.GET, EXPECTED_URL, body=b"GRIB_DATA", status=200)
        grib = NoaaGribFile(REF_TIME, 6, 3, cache_dir=tmp_path)
        with patch("noaa_gfs_wave.grib_file.open_dataset") as mock_open:
            mock_ds = MagicMock()
            mock_open.return_value = mock_ds
            result = grib.open_dataset()
        assert result is mock_ds


class TestNoaaGribFileLatest:
    def test_latest_uses_latest_available_cycle(self, tmp_path: Path):
        ref = datetime(2026, 3, 9, 6, 0, 0, tzinfo=UTC)
        with patch("noaa_gfs_wave.grib_file.latest_available_cycle", return_value=(ref, 6)):
            grib = NoaaGribFile.latest(forecast_hour=3, cache_dir=tmp_path)
        assert grib.reference_time == ref
        assert grib.cycle == 6
        assert grib.forecast_hour == 3

    def test_latest_accepts_now_override(self, tmp_path: Path):
        ref = datetime(2026, 3, 9, 0, 0, 0, tzinfo=UTC)
        now = datetime(2026, 3, 9, 12, 0, 0, tzinfo=UTC)
        with patch("noaa_gfs_wave.grib_file.latest_available_cycle", return_value=(ref, 0)) as mock_cycle:
            NoaaGribFile.latest(forecast_hour=3, cache_dir=tmp_path, now=now)
        mock_cycle.assert_called_once_with(now)


class TestNoaaGribFileFromLocal:
    def test_from_local_sets_local_path(self, tmp_path: Path):
        p = tmp_path / "my.grib2"
        p.write_bytes(b"GRIB")
        grib = NoaaGribFile.from_local(p)
        assert grib.local_path == p

    def test_from_local_exists_returns_true(self, tmp_path: Path):
        p = tmp_path / "my.grib2"
        p.write_bytes(b"GRIB")
        grib = NoaaGribFile.from_local(p)
        assert grib.exists()

    def test_from_local_read_opens_file(self, tmp_path: Path):
        p = tmp_path / "my.grib2"
        p.write_bytes(b"GRIB")
        grib = NoaaGribFile.from_local(p)
        with patch("noaa_gfs_wave.grib_file.open_dataset") as mock_open:
            mock_open.return_value = MagicMock()
            result = grib.read()
        assert isinstance(result, WaveGrid)
        mock_open.assert_called_once_with(str(p))
