"""xarray/cfgrib dataset helpers.

Internal module — not part of the public API. Helpers are thin wrappers
that isolate NaN-handling and xarray access patterns.
"""

import math
from typing import Any

import numpy as np


def to_float_or_none(x: Any) -> float | None:
    """Convert a scalar value to float, returning None for NaN or unconvertible values."""
    try:
        f = float(x)
        return None if math.isnan(f) else f
    except (TypeError, ValueError):
        return None


def scalar(ds: Any, name: str) -> float | None:
    """Extract a scalar float from a dataset variable, or None if missing/NaN."""
    if name not in ds:
        return None
    try:
        val = ds[name].values
        if getattr(val, "shape", None) == ():
            return to_float_or_none(val.item())
        return to_float_or_none(val)
    except (KeyError, AttributeError, ValueError):
        return None


def partition(ds: Any, name: str, idx: int) -> float | None:
    """Extract the idx-th element from a partition array variable."""
    if name not in ds:
        return None
    try:
        arr = np.asarray(ds[name].values).ravel()
        if idx < arr.size:
            return to_float_or_none(arr[idx])
        return None
    except (AttributeError, TypeError):
        return None


def time_str_or_none(da_name: str, ds: Any) -> str | None:
    """Extract a time coordinate as an ISO string, or None if missing."""
    if da_name not in ds:
        return None
    try:
        return str(ds[da_name].values.item())
    except (AttributeError, ValueError):
        return None


def open_dataset(path: str) -> Any:
    """Open a GRIB2 file as an xarray Dataset using cfgrib engine."""
    import xarray as xr

    return xr.open_dataset(path, engine="cfgrib", decode_timedelta=False)
