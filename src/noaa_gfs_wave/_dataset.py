"""xarray/cfgrib dataset helpers — stub."""

import math
from typing import Any

import numpy as np


def to_float_or_none(x: Any) -> float | None:
    raise NotImplementedError


def scalar(ds: Any, name: str) -> float | None:
    raise NotImplementedError


def partition(ds: Any, name: str, idx: int) -> float | None:
    raise NotImplementedError


def time_str_or_none(da_name: str, ds: Any) -> str | None:
    raise NotImplementedError


def open_dataset(path: str) -> Any:
    raise NotImplementedError
