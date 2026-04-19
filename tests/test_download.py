from pathlib import Path
from unittest.mock import patch

import pytest
import responses as responses_lib

from noaa_gfs_wave._download import download_to
from noaa_gfs_wave.exceptions import GribCorruptError, GribDownloadError, GribNotPublishedError

TEST_URL = "https://nomads.ncep.noaa.gov/test/sample.grib2"

VALID_GRIB_BODY = b"GRIB" + b"\x00" * 100 + b"7777"


class TestDownloadTo:
    @responses_lib.activate
    def test_happy_path_writes_file(self, tmp_path: Path):
        responses_lib.add(responses_lib.GET, TEST_URL, body=VALID_GRIB_BODY, status=200)
        dest = tmp_path / "out.grib2"
        download_to(TEST_URL, dest)
        assert dest.exists()
        assert dest.read_bytes() == VALID_GRIB_BODY

    @responses_lib.activate
    def test_atomic_write_no_partial_on_success(self, tmp_path: Path):
        responses_lib.add(responses_lib.GET, TEST_URL, body=VALID_GRIB_BODY, status=200)
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
        responses_lib.add(responses_lib.GET, TEST_URL, body=VALID_GRIB_BODY, status=200)
        dest = tmp_path / "subdir" / "out.grib2"
        download_to(TEST_URL, dest)
        assert dest.exists()

    @responses_lib.activate
    def test_request_timeout_passed_through(self, tmp_path: Path):
        responses_lib.add(responses_lib.GET, TEST_URL, body=VALID_GRIB_BODY, status=200)
        dest = tmp_path / "out.grib2"
        with patch("noaa_gfs_wave._download.requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.content = VALID_GRIB_BODY
            mock_get.return_value.headers = {"Content-Length": str(len(VALID_GRIB_BODY))}
            download_to(TEST_URL, dest, request_timeout=60)
            mock_get.assert_called_once_with(TEST_URL, timeout=60)


class TestIntegrityChecks:
    @responses_lib.activate
    def test_content_length_mismatch_raises_grib_corrupt_error(self, tmp_path: Path):
        short_body = b"GRIB" + b"\x00" * 100 + b"7777"  # 108 bytes, but we advertise 1000
        responses_lib.add(
            responses_lib.GET,
            TEST_URL,
            body=short_body,
            status=200,
            headers={"Content-Length": "1000"},
        )
        dest = tmp_path / "out.grib2"
        with pytest.raises(GribCorruptError):
            download_to(TEST_URL, dest)
        assert not Path(str(dest) + ".partial").exists()

    @responses_lib.activate
    def test_missing_content_length_skips_size_check(self, tmp_path: Path):
        responses_lib.add(responses_lib.GET, TEST_URL, body=VALID_GRIB_BODY, status=200)
        dest = tmp_path / "out.grib2"
        download_to(TEST_URL, dest)  # must not raise
        assert dest.exists()

    @responses_lib.activate
    def test_bad_head_magic_raises_grib_corrupt_error(self, tmp_path: Path):
        html_body = b"<!DOCTYPE html><html>" + b"x" * 87 + b"7777"
        responses_lib.add(
            responses_lib.GET,
            TEST_URL,
            body=html_body,
            status=200,
            headers={"Content-Length": str(len(html_body))},
        )
        dest = tmp_path / "out.grib2"
        with pytest.raises(GribCorruptError):
            download_to(TEST_URL, dest)
        assert not Path(str(dest) + ".partial").exists()

    @responses_lib.activate
    def test_bad_tail_magic_raises_grib_corrupt_error(self, tmp_path: Path):
        bad_tail_body = b"GRIB" + b"\x00" * 100 + b"XXXX"
        responses_lib.add(
            responses_lib.GET,
            TEST_URL,
            body=bad_tail_body,
            status=200,
            headers={"Content-Length": str(len(bad_tail_body))},
        )
        dest = tmp_path / "out.grib2"
        with pytest.raises(GribCorruptError):
            download_to(TEST_URL, dest)
        assert not Path(str(dest) + ".partial").exists()

    @responses_lib.activate
    def test_file_too_small_raises_grib_corrupt_error(self, tmp_path: Path):
        responses_lib.add(
            responses_lib.GET,
            TEST_URL,
            body=b"GRIB",
            status=200,
            headers={"Content-Length": "4"},
        )
        dest = tmp_path / "out.grib2"
        with pytest.raises(GribCorruptError):
            download_to(TEST_URL, dest)

    @responses_lib.activate
    def test_valid_grib_passes_all_checks(self, tmp_path: Path):
        responses_lib.add(
            responses_lib.GET,
            TEST_URL,
            body=VALID_GRIB_BODY,
            status=200,
            headers={"Content-Length": str(len(VALID_GRIB_BODY))},
        )
        dest = tmp_path / "out.grib2"
        download_to(TEST_URL, dest)
        assert dest.exists()
        assert dest.read_bytes() == VALID_GRIB_BODY
