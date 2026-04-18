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

WW3 uses NaN to mark land grid points. `WaveGrid.at()` on a land point returns a `WW3PointForecast` where all numeric fields are `None`.

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

## Limitations

- Wave model only (no GFS atmospheric, HRRR, NAM, RTOFS)
- No async API
- Local filesystem cache only (no S3 / R2)
- Nearest-neighbor extraction only (no interpolation)
- No automatic retry — callers own retry logic

## Development

```bash
git clone https://github.com/fbenevides/noaa-gfs-wave
cd noaa-gfs-wave
python -m venv .venv && source .venv/bin/activate
pip install -e ".[test,dev]"
pytest
ruff check .
```

## License

MIT — see [LICENSE](LICENSE).

## Attribution

GFS wave data is provided by NOAA and is in the public domain. This library is not affiliated with NOAA.
