# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-04-18

### Added

- `NoaaGribFile` — lazy download and cached GRIB2 access with `.read()`, `.open_dataset()`, `.exists()`, `.download()`
- `NoaaGribFile.latest()` — resolve and construct the most recently published GFS wave cycle
- `NoaaGribFile.from_local()` — wrap an existing on-disk GRIB2 file without network access
- `WaveGrid` — in-memory xarray-backed wrapper with typed array accessors and `at(lat, lon)` nearest-neighbor extraction
- `WW3PointForecast` and supporting pydantic models: `WW3PointMeta`, `Wind10m`, `CombinedSea`, `DominantSystem`, `WindSea`, `SwellPartition`
- `latest_available_cycle()` — detect the most recently published GFS wave cycle with 9-hour publication lag
- `NOAA_CYCLES` constant — `[0, 6, 12, 18]`
- Exception hierarchy: `NoaaGfsWaveError`, `GribDownloadError`, `GribNotPublishedError`, `GribCorruptError`
- Atomic download writes (`.partial` → rename)
- Configurable `request_timeout` (default 30 s)
- `tests/fixtures/sample.grib2` — real 55 KB cropped GRIB2 fixture for integration testing
