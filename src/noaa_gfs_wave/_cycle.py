"""GFS cycle detection utilities — stub (will be implemented in green commit)."""

from datetime import datetime

NOAA_CYCLES: list[int] = []


def latest_available_cycle(now: datetime | None = None) -> tuple[datetime, int]:
    raise NotImplementedError
