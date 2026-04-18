"""Tests for _dataset.py helper functions — NaN and exception handling."""

from unittest.mock import MagicMock

import numpy as np
import pytest

from noaa_gfs_wave._dataset import partition, scalar, time_str_or_none, to_float_or_none


class TestToFloatOrNone:
    def test_normal_float(self):
        assert to_float_or_none(1.5) == pytest.approx(1.5)

    def test_nan_returns_none(self):
        assert to_float_or_none(float("nan")) is None

    def test_numpy_nan_returns_none(self):
        assert to_float_or_none(np.nan) is None

    def test_unconvertible_returns_none(self):
        assert to_float_or_none("not_a_number") is None

    def test_zero_returns_zero(self):
        assert to_float_or_none(0.0) == 0.0

    def test_none_input_returns_none(self):
        assert to_float_or_none(None) is None

    def test_integer_converts_to_float(self):
        result = to_float_or_none(5)
        assert isinstance(result, float)
        assert result == 5.0


class TestScalar:
    def _build_ds(self, name: str, value):
        """Build a minimal mock dataset for scalar() testing."""
        da = MagicMock()
        val = np.array(value)
        da.values = val

        ds = {}
        ds[name] = da
        return ds

    def test_returns_float_for_scalar_value(self):
        ds = self._build_ds("swh", 1.5)
        result = scalar(ds, "swh")
        assert result == pytest.approx(1.5)

    def test_returns_none_for_nan(self):
        ds = self._build_ds("swh", np.nan)
        result = scalar(ds, "swh")
        assert result is None

    def test_returns_none_for_missing_key(self):
        ds = {}
        result = scalar(ds, "swh")
        assert result is None

    def test_handles_exception_in_values(self):
        da = MagicMock()
        # Make .values raise an exception when accessed
        type(da).values = property(lambda self: (_ for _ in ()).throw(RuntimeError("broken")))
        ds = {"swh": da}
        result = scalar(ds, "swh")
        assert result is None


class TestPartition:
    def _build_ds(self, name: str, arr):
        da = MagicMock()
        da.values = np.array(arr, dtype=np.float32)
        return {name: da}

    def test_returns_first_element(self):
        ds = self._build_ds("shts", [1.0, 2.0, 3.0])
        assert partition(ds, "shts", 0) == pytest.approx(1.0)

    def test_returns_second_element(self):
        ds = self._build_ds("shts", [1.0, 2.0, 3.0])
        assert partition(ds, "shts", 1) == pytest.approx(2.0)

    def test_returns_none_for_out_of_bounds(self):
        ds = self._build_ds("shts", [1.0])
        assert partition(ds, "shts", 5) is None

    def test_returns_none_for_missing_key(self):
        assert partition({}, "shts", 0) is None

    def test_returns_none_for_nan_element(self):
        ds = self._build_ds("shts", [np.nan])
        assert partition(ds, "shts", 0) is None

    def test_handles_exception_in_values(self):
        da = MagicMock()
        type(da).values = property(lambda self: (_ for _ in ()).throw(RuntimeError("broken")))
        result = partition({"shts": da}, "shts", 0)
        assert result is None


class TestTimeStrOrNone:
    def test_returns_string(self):
        da = MagicMock()
        da.values = MagicMock()
        da.values.item.return_value = "2026-03-09T06:00:00"
        result = time_str_or_none("valid_time", {"valid_time": da})
        assert isinstance(result, str)
        assert "2026-03-09" in result

    def test_returns_none_for_missing_key(self):
        assert time_str_or_none("valid_time", {}) is None

    def test_returns_none_on_exception(self):
        da = MagicMock()
        da.values = MagicMock()
        da.values.item.side_effect = RuntimeError("broken")
        assert time_str_or_none("valid_time", {"valid_time": da}) is None
