"""Atomic HTTP download helper.

Downloads a GRIB2 file from a URL to a local path using an atomic
`.partial` → rename write to prevent corrupt partial files on retry.
"""

from pathlib import Path

import requests

from noaa_gfs_wave.exceptions import GribCorruptError, GribDownloadError, GribNotPublishedError

_GRIB_HEAD = b"GRIB"
_GRIB_TAIL = b"7777"
_GRIB_MIN_SIZE = 8


def download_to(url: str, dest: Path, *, request_timeout: int = 30) -> None:
    """Download `url` to `dest` atomically.

    Raises:
        GribNotPublishedError: HTTP 404 — cycle not yet on NOMADS.
        GribDownloadError: any other HTTP error or network failure.
        GribCorruptError: downloaded bytes fail integrity checks.
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
    _write_and_verify(response, dest, partial)


def _check_response(response: requests.Response, url: str) -> None:
    if response.status_code == 404:
        raise GribNotPublishedError(f"GRIB not yet published (404): {url}")
    if response.status_code != 200:
        raise GribDownloadError(f"Unexpected HTTP {response.status_code} fetching {url}")


def _write_and_verify(response: requests.Response, dest: Path, partial: Path) -> None:
    raw = response.headers.get("Content-Length")
    expected_size = int(raw) if raw is not None else None
    try:
        partial.write_bytes(response.content)
        _verify_grib_bytes(partial, expected_size=expected_size)
        partial.replace(dest)
    except (OSError, GribCorruptError):
        partial.unlink(missing_ok=True)
        raise


def _verify_grib_bytes(path: Path, *, expected_size: int | None) -> None:
    """Raise GribCorruptError if path is not a valid GRIB2 of expected size."""
    size = path.stat().st_size
    if expected_size is not None and size != expected_size:
        raise GribCorruptError(
            f"downloaded size {size} does not match Content-Length {expected_size}"
        )
    if size < _GRIB_MIN_SIZE:
        raise GribCorruptError("file too small to be a valid GRIB2")
    with path.open("rb") as fh:
        head = fh.read(4)
        fh.seek(-4, 2)
        tail = fh.read(4)
    if head != _GRIB_HEAD or tail != _GRIB_TAIL:
        raise GribCorruptError("file is not a valid GRIB2 (magic bytes mismatch)")
