"""Escape hatch — open the underlying xarray.Dataset directly for advanced use.

Useful when you need xarray operations the typed API doesn't expose
(full-grid statistics, slicing, saving to NetCDF, etc.).

Run: uv run python examples/raw_xarray.py
"""

from noaa_gfs_wave import NoaaGribFile


def main() -> None:
    grib = NoaaGribFile.latest(forecast_hour=3, cache_dir="./noaa_cache")
    ds = grib.open_dataset()
    try:
        print("variables :", sorted(ds.data_vars))
        print("dims      :", dict(ds.sizes))
        swh = ds.swh
        print(f"swh range : {float(swh.min()):.2f}..{float(swh.max()):.2f} m")
        print(f"swh mean  : {float(swh.mean()):.2f} m  (NaN-skipped)")
    finally:
        ds.close()


if __name__ == "__main__":
    main()
