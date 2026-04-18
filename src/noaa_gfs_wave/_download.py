"""Atomic HTTP download helper.

Downloads a GRIB2 file from a URL to a local path using an atomic
`.partial` → rename write to prevent corrupt partial files on retry.
"""

from pathlib import Path

import requests

from noaa_gfs_wave.exceptions import GribDownloadError, GribNotPublishedError


def download_to(url: str, dest: Path, *, request_timeout: int = 30) -> None:
    """Download `url` to `dest` atomically.

    Raises:
        GribNotPublishedError: HTTP 404 — cycle not yet on NOMADS.
        GribDownloadError: any other HTTP error or network failure.
        OSError: if `dest.parent` is unwritable.
    """
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    partial = Path(str(dest) + ".partial")

    try:
        response = requests.get(url, timeout=request_timeout)
    except requests.RequestException as exc:
        raise GribDownloadError(f"Network error fetching {url}: {exc}") from exc

    _check_response(response, url)
    _write_atomic(response.content, dest, partial)


def _check_response(response: requests.Response, url: str) -> None:
    if response.status_code == 404:
        raise GribNotPublishedError(f"GRIB not yet published (404): {url}")
    if response.status_code != 200:
        raise GribDownloadError(f"Unexpected HTTP {response.status_code} fetching {url}")


def _write_atomic(content: bytes, dest: Path, partial: Path) -> None:
    try:
        partial.write_bytes(content)
        partial.replace(dest)
    except Exception:
        partial.unlink(missing_ok=True)
        raise
