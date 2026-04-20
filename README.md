# noaa-gfs-wave

Read NOAA GFS WaveWatch III forecasts without the plumbing.

## Install

```bash
pip install noaa-gfs-wave
```

### System dependency — ecCodes

`cfgrib` (used to parse GRIB2 files) requires the ecCodes C library:

```bash
# macOS
brew install eccodes

# Debian/Ubuntu
apt-get install libeccodes-dev
```

On recent `cfgrib` versions the wheel bundles a binary `eccodeslib`, so the system package may not be strictly required — but install it if you see errors.

## Quickstart

```python
from noaa_gfs_wave import NoaaGribFile, latest_available_cycle

# From the latest published cycle (detects automatically)
grib = NoaaGribFile.latest(forecast_hour=3)
grid = grib.read()
point = grid.at(lat=-9.1, lon=-35.2)
print(point.combined.significant_height_meters)
print(point.wind10m.speed_meters_per_second, point.wind10m.speed_knots)
print(point.power_kilowatts_per_meter)  # kW per meter of wave crest

# Explicit cycle
from datetime import datetime, UTC
ref_time = datetime(2026, 3, 9, 0, 0, 0, tzinfo=UTC)
grib = NoaaGribFile(reference_time=ref_time, cycle=6, forecast_hour=3, cache_dir="./cache")
grid = grib.read()

# From a local file (offline / testing)
grib = NoaaGribFile.from_local("path/to/file.grib2")
grid = grib.read()
point = grid.at(lat=-9.1, lon=-35.2)

# xarray escape hatch
ds = grib.open_dataset()
print(ds.swh)
ds.close()
```

## Custom base URL (mirrors, testing)

By default, all downloads hit NOAA NOMADS. To point at an internal mirror or
a test server (useful when NOMADS is rate-limiting or unavailable), pass
`base_url` to either `GribAddress` or `NoaaGribFile`.

```python
from noaa_gfs_wave import GribAddress, NoaaGribFile, NOAA_NOMADS_BASE_URL
from datetime import datetime, UTC

ref_time = datetime(2026, 3, 9, 0, 0, 0, tzinfo=UTC)

# Default — hits NOAA NOMADS
address = GribAddress(reference_time=ref_time, cycle=12, forecast_hour=3)
url = address.remote_url()  # https://nomads.ncep.noaa.gov/...

# Custom mirror via GribAddress
address = GribAddress(
    reference_time=ref_time,
    cycle=12,
    forecast_hour=3,
    base_url="https://my-mirror.example/gfs",
)

# Same knob on NoaaGribFile
grib = NoaaGribFile(
    reference_time=ref_time,
    cycle=12,
    forecast_hour=3,
    base_url="https://my-mirror.example/gfs",
)
```

`NOAA_NOMADS_BASE_URL` is the canonical base URL string and can be imported
directly if you need to construct URLs manually.

## API Reference

| Name | Type | Description |
|------|------|-------------|
| `NoaaGribFile` | class | Lazy download + cached GRIB2 access |
| `WaveGrid` | class | In-memory xarray-backed grid with typed accessors |
| `WW3PointForecast` | pydantic model | Full forecast for a single grid point |
| `WW3PointMeta` | pydantic model | Timing and location metadata |
| `Wind10m` | pydantic model | 10 m wind conditions |
| `CombinedSea` | pydantic model | Combined (total) sea state |
| `DominantSystem` | pydantic model | Highest-energy wave system |
| `WindSea` | pydantic model | Locally generated wind-driven waves |
| `SwellPartition` | pydantic model | One of three swell partitions |
| `latest_available_cycle` | function | Returns `(datetime, int)` for the latest published cycle |
| `NOAA_CYCLES` | constant | `[0, 6, 12, 18]` |
| `NoaaGfsWaveError` | exception | Base exception |
| `GribDownloadError` | exception | Network or HTTP error during download |
| `GribNotPublishedError` | exception | HTTP 404 — cycle not yet on NOMADS |
| `GribCorruptError` | exception | cfgrib parse failure |

## Concepts

### GFS cycle publication lag

The GFS wave model runs at 0z, 6z, 12z, and 18z UTC. Each cycle takes ~9 hours to appear on NOMADS. `latest_available_cycle()` accounts for this lag automatically.

### Longitude convention (0..360)

The NOAA WW3 grid uses longitudes in `0..360` (not `-180..180`). `WaveGrid.at()` accepts both conventions — negative values are normalized automatically. `WaveGrid.longitudes` returns the raw `0..360` array.

### NaN over land

WW3 uses NaN to mark land grid points. `WaveGrid.at()` on a land point returns a `WW3PointForecast` where all numeric fields are `None`. Use `is_land()` to check this without inspecting individual fields:

```python
point = grid.at(lat=-7.0, lon=-35.0)
if point.is_land():
    ...
```

### Nearest-neighbor extraction

`WaveGrid.at(lat, lon)` uses `np.argmin` on both axes — no bilinear interpolation. This avoids smearing land NaN values into ocean points near coastlines.

## Caching

Files are stored flat in `cache_dir` with the naming convention:

```
{cache_dir}/{YYYYMMDD}_{CC}_{FFF}.grib2
```

cfgrib generates an index sidecar (`*.idx`) automatically. Include `*.idx` in cleanup if you evict GRIB files. The library does not manage cache eviction.

## Error Handling

| Situation | Exception |
|-----------|-----------|
| HTTP 404 — cycle not yet published | `GribNotPublishedError` |
| 5xx, network error, timeout | `GribDownloadError` |
| cfgrib can't parse the file | `GribCorruptError` |
| `cache_dir` unwritable | `OSError` (unchanged) |

Downloaded files are verified for completeness (`Content-Length` match) and GRIB2 framing (`GRIB` head, `7777` tail) before being committed to the cache. A mismatch raises `GribCorruptError` and the `.partial` file is discarded so the cache stays clean.

## Limitations

- Wave model only (no GFS atmospheric, HRRR, NAM, RTOFS)
- No async API
- Local filesystem cache only (no S3 / R2)
- Nearest-neighbor extraction only (no interpolation)
- No automatic retry — callers own retry logic

## Development

The library is built with hatchling; dev and CI use uv for fast, reproducible installs.

```bash
git clone https://github.com/fbenevides/noaa-gfs-wave
cd noaa-gfs-wave
uv sync --all-extras
uv run pytest
uv run ruff check .
```

End-users who aren't on uv can still install with pip:

```bash
pip install noaa-gfs-wave
```

## License

MIT — see [LICENSE](LICENSE).

## Attribution

GFS wave data is provided by NOAA and is in the public domain. This library is not affiliated with NOAA.
