"""Unit tests for cross-platform timestamp helpers."""

import sys
from datetime import datetime
from pathlib import Path

import pytest

from audiopyle import timestamps


@pytest.fixture
def fx_file(tmp_path: Path) -> Path:
    """A throwaway file with known initial mtime."""
    p = tmp_path / "sample.bin"
    p.write_bytes(b"hello")
    return p


def test_get_mtime_returns_datetime(fx_file: Path) -> None:
    """`get_mtime` returns a naive datetime corresponding to the file's mtime."""
    result = timestamps.get_mtime(fx_file)
    assert isinstance(result, datetime)


def test_set_and_get_mtime_round_trip(fx_file: Path) -> None:
    """Setting mtime and reading it back yields the same value (to the second)."""
    target = datetime(2020, 6, 15, 12, 0, 0)
    timestamps.set_mtime(fx_file, target)
    result = timestamps.get_mtime(fx_file)
    assert result.replace(microsecond=0) == target


def test_get_creation_time_returns_datetime(fx_file: Path) -> None:
    """`get_creation_time` returns a datetime on every platform."""
    result = timestamps.get_creation_time(fx_file)
    assert isinstance(result, datetime)


@pytest.mark.skipif(sys.platform != "win32", reason="creation time is only writable on Windows")
def test_set_creation_time_windows(fx_file: Path) -> None:
    """On Windows, `set_creation_time` actually changes the file's birth time."""
    target = datetime(2020, 6, 15, 12, 0, 0)
    timestamps.set_creation_time(fx_file, target)
    result = timestamps.get_creation_time(fx_file)
    assert result.replace(microsecond=0) == target


@pytest.mark.skipif(
    sys.platform == "win32",
    reason="POSIX systems do not expose writable birth time",
)
def test_set_creation_time_noop_on_posix(fx_file: Path) -> None:
    """On POSIX, `set_creation_time` is a no-op and must not raise."""
    timestamps.set_creation_time(fx_file, datetime(2020, 6, 15, 12, 0, 0))
