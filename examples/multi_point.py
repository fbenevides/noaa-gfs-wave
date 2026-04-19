"""Query many spots from the same cycle — load the grid once, reuse for every point.

Run: uv run python examples/multi_point.py
"""

from noaa_gfs_wave import NoaaGribFile, WaveGrid

SPOTS: dict[str, tuple[float, float]] = {
    "Pipeline, Oahu": (21.66, -158.05),
    "Nazaré, Portugal": (39.60, -9.07),
    "Ipanema, Rio": (-22.98, -43.21),
    "Tibau do Sul, BR": (-6.23, -35.05),
    "Bells Beach, AUS": (-38.37, 144.28),
    "Jeffreys Bay, ZA": (-34.05, 24.93),
}


def main() -> None:
    grib = NoaaGribFile.latest(forecast_hour=3, cache_dir="./noaa_cache")
    grid = grib.read()
    print(f"cycle {grib.reference_time.date()} {grib.cycle:02d}z +{grib.forecast_hour}h\n")
    print(f"{'spot':22s} {'Hs(m)':>6} {'T(s)':>5} {'dir':>4}")
    for name, (lat, lon) in SPOTS.items():
        print_row(grid, name, lat, lon)


def print_row(grid: WaveGrid, name: str, lat: float, lon: float) -> None:
    point = grid.at(lat=lat, lon=lon)
    if point.is_land():
        print(f"{name:22s} {'land':>17s}")
        return
    print(
        f"{name:22s} "
        f"{point.combined.significant_height_meters:>6.2f} "
        f"{point.dominant.period_seconds:>5.1f} "
        f"{point.dominant.direction_degrees_from:>4.0f}"
    )


if __name__ == "__main__":
    main()
