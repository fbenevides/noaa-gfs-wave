from pathlib import Path
from unittest.mock import patch

import pytest
import responses as responses_lib

from noaa_gfs_wave._download import download_to
from noaa_gfs_wave.exceptions import GribDownloadError, GribNotPublishedError

TEST_URL = "https://nomads.ncep.noaa.gov/test/sample.grib2"


class TestDownloadTo:
    @responses_lib.activate
    def test_happy_path_writes_file(self, tmp_path: Path):
        responses_lib.add(responses_lib.GET, TEST_URL, body=b"GRIB_DATA", status=200)
        dest = tmp_path / "out.grib2"
        download_to(TEST_URL, dest)
        assert dest.exists()
        assert dest.read_bytes() == b"GRIB_DATA"

    @responses_lib.activate
    def test_atomic_write_no_partial_on_success(self, tmp_path: Path):
        responses_lib.add(responses_lib.GET, TEST_URL, body=b"DATA", status=200)
        dest = tmp_path / "out.grib2"
        download_to(TEST_URL, dest)
        partial = Path(str(dest) + ".partial")
        assert not partial.exists()

    @responses_lib.activate
    def test_404_raises_grib_not_published(self, tmp_path: Path):
        responses_lib.add(responses_lib.GET, TEST_URL, status=404)
        with pytest.raises(GribNotPublishedError):
            download_to(TEST_URL, tmp_path / "out.grib2")

    @responses_lib.activate
    def test_500_raises_grib_download_error(self, tmp_path: Path):
        responses_lib.add(responses_lib.GET, TEST_URL, status=500)
        with pytest.raises(GribDownloadError):
            download_to(TEST_URL, tmp_path / "out.grib2")

    @responses_lib.activate
    def test_network_error_raises_grib_download_error(self, tmp_path: Path):
        import requests

        responses_lib.add(responses_lib.GET, TEST_URL, body=requests.ConnectionError("timeout"))
        with pytest.raises(GribDownloadError):
            download_to(TEST_URL, tmp_path / "out.grib2")

    @responses_lib.activate
    def test_no_partial_file_left_on_404(self, tmp_path: Path):
        responses_lib.add(responses_lib.GET, TEST_URL, status=404)
        dest = tmp_path / "out.grib2"
        with pytest.raises(GribNotPublishedError):
            download_to(TEST_URL, dest)
        partial = Path(str(dest) + ".partial")
        assert not partial.exists()

    @responses_lib.activate
    def test_creates_parent_directory(self, tmp_path: Path):
        responses_lib.add(responses_lib.GET, TEST_URL, body=b"DATA", status=200)
        dest = tmp_path / "subdir" / "out.grib2"
        download_to(TEST_URL, dest)
        assert dest.exists()

    @responses_lib.activate
    def test_request_timeout_passed_through(self, tmp_path: Path):
        responses_lib.add(responses_lib.GET, TEST_URL, body=b"DATA", status=200)
        dest = tmp_path / "out.grib2"
        with patch("noaa_gfs_wave._download.requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.content = b"DATA"
            download_to(TEST_URL, dest, request_timeout=60)
            mock_get.assert_called_once_with(TEST_URL, timeout=60)
