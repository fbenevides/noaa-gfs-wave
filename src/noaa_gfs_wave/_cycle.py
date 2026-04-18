"""GFS cycle detection utilities.

Provides helpers for determining the most recently published NOAA GFS wave cycle.
The GFS wave model runs at 0z, 6z, 12z, and 18z UTC. Each cycle takes ~9 hours
to be fully published on NOMADS after the model run time.
"""

from datetime import UTC, datetime, timedelta

NOAA_CYCLES = [0, 6, 12, 18]
_PUBLICATION_LAG_HOURS = 9
_LOOKBACK_HOURS = 48


def latest_available_cycle(now: datetime | None = None) -> tuple[datetime, int]:
    """Return (reference_time, cycle) for the most recently published GFS wave cycle.

    Scans up to 48 hours back to find a cycle whose publication window has elapsed.
    Raises RuntimeError if no valid cycle is found within the lookback window.
    """
    if now is None:
        now = datetime.now(UTC)

    for hours_back in range(0, _LOOKBACK_HOURS):
        candidate = now - timedelta(hours=hours_back)
        cycle = (candidate.hour // 6) * 6
        cycle_time = candidate.replace(hour=cycle, minute=0, second=0, microsecond=0)
        if now >= cycle_time + timedelta(hours=_PUBLICATION_LAG_HOURS):
            return cycle_time, cycle

    raise RuntimeError("Could not determine a valid GFS cycle within the last 48 hours")
