"""Build a forecast timeseries for one point across multiple forecast hours.

Each hour triggers a separate download; subsequent runs hit the local cache.

Run: uv run python examples/forecast_timeseries.py
"""

from datetime import UTC

from noaa_gfs_wave import NoaaGribFile, WW3PointForecast, latest_available_cycle

LAT = 21.66
LON = -158.05
HORIZON = [0, 3, 6, 9, 12, 18, 24, 48, 72]


def main() -> None:
    ref_time, cycle = latest_available_cycle()
    print(f"cycle {ref_time.date()} {cycle:02d}z  point ({LAT}, {LON})\n")
    print(f"{'+h':>4} {'valid':20s} {'Hs(m)':>6} {'T(s)':>5} {'dir':>4}")
    for fh in HORIZON:
        grib = NoaaGribFile(ref_time, cycle, fh, cache_dir="./noaa_cache")
        point = grib.read().at(lat=LAT, lon=LON)
        print_row(fh, point)


def print_row(forecast_hour: int, point: WW3PointForecast) -> None:
    if point.is_land():
        return
    valid = point.forecast_date.astimezone(UTC).strftime("%Y-%m-%d %H:%MZ")
    print(
        f"{forecast_hour:>4} {valid:20s} "
        f"{point.combined.significant_height_meters:>6.2f} "
        f"{point.dominant.period_seconds:>5.1f} "
        f"{point.dominant.direction_degrees_from:>4.0f}"
    )


if __name__ == "__main__":
    main()
