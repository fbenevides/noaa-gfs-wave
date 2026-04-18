"""Atomic HTTP download helper — stub."""

from pathlib import Path


def download_to(url: str, dest: Path, *, request_timeout: int = 30) -> None:
    raise NotImplementedError
