"""Fetch the latest published GFS wave cycle and print a forecast for one point.

Run: uv run python examples/latest_forecast.py
"""

from noaa_gfs_wave import NoaaGribFile, WW3PointForecast

LAT = 21.66
LON = -158.05


def main() -> None:
    grib = NoaaGribFile.latest(forecast_hour=3, cache_dir="./noaa_cache")
    print(f"cycle   : {grib.reference_time.date()} {grib.cycle:02d}z +{grib.forecast_hour}h")
    print(f"cached  : {grib.local_path}")

    point = grib.read().at(lat=LAT, lon=LON)
    print_point(point, LAT, LON)


def print_point(point: WW3PointForecast, lat: float, lon: float) -> None:
    if point.is_land():
        print(f"({lat}, {lon}) is a land grid point")
        return
    print(f"valid   : {point.forecast_date.isoformat()}")
    print(f"  Hs    : {point.combined.significant_height_meters:.2f} m")
    print(f"  period: {point.dominant.period_seconds:.1f} s")
    print(f"  dir   : {point.dominant.direction_degrees_from:.0f} deg (from)")
    print(
        f"  wind  : {point.wind10m.speed_meters_per_second:.1f} m/s ({point.wind10m.speed_knots:.1f} kn)"
    )


if __name__ == "__main__":
    main()
