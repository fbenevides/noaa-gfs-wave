# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.1] - 2026-04-19

### Added

- ([92a59ce](https://github.com/fbenevides/noaa-gfs-wave/commit/92a59ce)) include commit sha link and author in changelog entries by @fbenevides
- ([866bf3b](https://github.com/fbenevides/noaa-gfs-wave/commit/866bf3b)) add release script for version bump and changelog by @fbenevides
- ([4403552](https://github.com/fbenevides/noaa-gfs-wave/commit/4403552)) verify grib magic bytes and content length on download by @fbenevides
- ([19ad4de](https://github.com/fbenevides/noaa-gfs-wave/commit/19ad4de)) add base_url kwarg to NoaaGribFile by @fbenevides
- ([9fecc49](https://github.com/fbenevides/noaa-gfs-wave/commit/9fecc49)) add configurable base_url to GribAddress by @fbenevides
- ([58a3b75](https://github.com/fbenevides/noaa-gfs-wave/commit/58a3b75)) replace addressing functions with GribAddress class by @fbenevides
- ([b9c0236](https://github.com/fbenevides/noaa-gfs-wave/commit/b9c0236)) add is_land helper on WW3PointForecast by @fbenevides
- ([14d9a23](https://github.com/fbenevides/noaa-gfs-wave/commit/14d9a23)) improve coverage with dataset helpers and wave grid property tests by @fbenevides
- ([9c3e563](https://github.com/fbenevides/noaa-gfs-wave/commit/9c3e563)) add grib fixture and integration tests by @fbenevides
- ([1c41f43](https://github.com/fbenevides/noaa-gfs-wave/commit/1c41f43)) wire full public api in __init__.py by @fbenevides
- ([12b5924](https://github.com/fbenevides/noaa-gfs-wave/commit/12b5924)) implement NoaaGribFile facade with lazy download and from_local by @fbenevides
- ([f3b22d4](https://github.com/fbenevides/noaa-gfs-wave/commit/f3b22d4)) implement wave grid with typed accessors and nearest-neighbor extraction by @fbenevides
- ([e699e11](https://github.com/fbenevides/noaa-gfs-wave/commit/e699e11)) port pydantic ww3 models without harper imports by @fbenevides
- ([2e5b216](https://github.com/fbenevides/noaa-gfs-wave/commit/2e5b216)) port grib addressing and download with typed exceptions by @fbenevides
- ([a9cd77b](https://github.com/fbenevides/noaa-gfs-wave/commit/a9cd77b)) port cycle detection by @fbenevides

### Fixed

- ([063f3c7](https://github.com/fbenevides/noaa-gfs-wave/commit/063f3c7)) assert version matches semver format instead of hardcoded string by @fbenevides
- ([0d2bc31](https://github.com/fbenevides/noaa-gfs-wave/commit/0d2bc31)) update mock response bodies to valid grib2 magic by @fbenevides
- ([92ce0f9](https://github.com/fbenevides/noaa-gfs-wave/commit/92ce0f9)) extract valid_time from dataset without lossy string roundtrip by @fbenevides
- ([b75c68f](https://github.com/fbenevides/noaa-gfs-wave/commit/b75c68f)) raise GribCorruptError on malformed valid_time by @fbenevides

### Changed

- ([763f752](https://github.com/fbenevides/noaa-gfs-wave/commit/763f752)) validate pr title against conventional commits in ci by @fbenevides
- ([dcd376e](https://github.com/fbenevides/noaa-gfs-wave/commit/dcd376e)) refresh uv lockfile after pinning changes by @fbenevides
- ([38ca610](https://github.com/fbenevides/noaa-gfs-wave/commit/38ca610)) pin test and dev dependencies to exact versions by @fbenevides
- ([aa630a2](https://github.com/fbenevides/noaa-gfs-wave/commit/aa630a2)) pin runtime dependencies to exact versions by @fbenevides
- ([70d08a5](https://github.com/fbenevides/noaa-gfs-wave/commit/70d08a5)) update author email in pyproject by @fbenevides
- ([9fc3b3b](https://github.com/fbenevides/noaa-gfs-wave/commit/9fc3b3b)) document integrity checks in readme by @fbenevides
- ([4a689a2](https://github.com/fbenevides/noaa-gfs-wave/commit/4a689a2)) drop empty tests/__init__.py by @fbenevides
- ([0b8938c](https://github.com/fbenevides/noaa-gfs-wave/commit/0b8938c)) document configurable base_url in readme by @fbenevides
- ([58aa598](https://github.com/fbenevides/noaa-gfs-wave/commit/58aa598)) expose GribAddress publicly by @fbenevides
- ([f2418dc](https://github.com/fbenevides/noaa-gfs-wave/commit/f2418dc)) rename _addressing to _grib_address to match class name by @fbenevides
- ([a1182c1](https://github.com/fbenevides/noaa-gfs-wave/commit/a1182c1)) document uv in readme by @fbenevides
- ([7c12bbd](https://github.com/fbenevides/noaa-gfs-wave/commit/7c12bbd)) migrate release workflow to uv by @fbenevides
- ([8b06c81](https://github.com/fbenevides/noaa-gfs-wave/commit/8b06c81)) migrate ci workflow to uv by @fbenevides
- ([4c0dd15](https://github.com/fbenevides/noaa-gfs-wave/commit/4c0dd15)) generate uv lockfile by @fbenevides
- ([8787f7e](https://github.com/fbenevides/noaa-gfs-wave/commit/8787f7e)) fix typo in ci install-system-dependencies step by @fbenevides
- ([87a563d](https://github.com/fbenevides/noaa-gfs-wave/commit/87a563d)) document is_land helper in readme by @fbenevides
- ([a25fd09](https://github.com/fbenevides/noaa-gfs-wave/commit/a25fd09)) broaden venv gitignore pattern by @fbenevides
- ([16897de](https://github.com/fbenevides/noaa-gfs-wave/commit/16897de)) tighten type hints and clean dead code by @fbenevides
- ([ea34cb9](https://github.com/fbenevides/noaa-gfs-wave/commit/ea34cb9)) narrow exception handlers to specific types by @fbenevides
- ([def79b7](https://github.com/fbenevides/noaa-gfs-wave/commit/def79b7)) write readme by @fbenevides
- ([63fd8f1](https://github.com/fbenevides/noaa-gfs-wave/commit/63fd8f1)) scaffold project by @fbenevides


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
