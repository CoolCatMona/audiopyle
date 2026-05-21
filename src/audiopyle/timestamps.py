"""Cross-platform helpers for reading and writing file timestamps.

The module exposes a small, opinionated surface:
* :func:`get_mtime` / :func:`set_mtime` use ``os.utime`` and ``Path.stat``.
* :func:`get_creation_time` returns the best available "birth" time on
  the current platform (``st_birthtime`` on macOS/BSD, win32 ``CreationTime``
  on Windows, ``st_ctime`` as a last resort on Linux).
* :func:`set_creation_time` only does anything on Windows; on POSIX it
  logs at DEBUG and returns without error.
"""

from __future__ import annotations

import logging
import os
import sys
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


def get_mtime(path: Path) -> datetime:
    """Return the modification time of ``path`` as a naive ``datetime``.

    Args:
        path: The file or directory to inspect.

    Returns:
        The file's mtime as a local-time naive ``datetime``.
    """
    return datetime.fromtimestamp(path.stat().st_mtime)


def set_mtime(path: Path, when: datetime) -> None:
    """Set the modification (and access) time of ``path`` to ``when``.

    Args:
        path: The file or directory to update.
        when: The naive ``datetime`` to use for both atime and mtime.
    """
    ts = when.timestamp()
    os.utime(path, (ts, ts))


def get_creation_time(path: Path) -> datetime:
    """Return the best-available creation time of ``path``.

    On macOS and BSD this is ``stat.st_birthtime``. On Windows this is the
    NTFS ``CreationTime`` field via pywin32. On Linux this falls back to
    ``stat.st_ctime`` (which is "change time", not creation time, but it is
    the closest available signal).

    Args:
        path: The file or directory to inspect.

    Returns:
        A naive ``datetime`` representing the creation time.
    """
    if sys.platform == "win32":
        return _windows_get_creation_time(path)
    stat = path.stat()
    birth = getattr(stat, "st_birthtime", None)
    if birth is not None:
        return datetime.fromtimestamp(birth)
    return datetime.fromtimestamp(stat.st_ctime)


def set_creation_time(path: Path, when: datetime) -> None:
    """Set the creation time of ``path`` to ``when``.

    On POSIX this is a no-op (the underlying filesystem does not expose a
    writable birth time). On Windows this updates the NTFS ``CreationTime``
    field via pywin32.

    Args:
        path: The file to update.
        when: The naive ``datetime`` to use as the creation time.
    """
    if sys.platform != "win32":
        logger.debug("set_creation_time is a no-op on %s", sys.platform)
        return
    _windows_set_creation_time(path, when)


def _windows_get_creation_time(path: Path) -> datetime:
    import win32con
    import win32file

    handle = win32file.CreateFile(
        str(path),
        win32con.GENERIC_READ,
        win32con.FILE_SHARE_READ,
        None,
        win32con.OPEN_EXISTING,
        win32con.FILE_ATTRIBUTE_NORMAL,
        None,
    )
    try:
        creation, _, _ = win32file.GetFileTime(handle)
    finally:
        handle.Close()
    return datetime.fromtimestamp(float(creation))


def _windows_set_creation_time(path: Path, when: datetime) -> None:
    import pywintypes
    import win32con
    import win32file

    handle = win32file.CreateFile(
        str(path),
        win32con.GENERIC_WRITE,
        win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE,
        None,
        win32con.OPEN_EXISTING,
        win32con.FILE_ATTRIBUTE_NORMAL,
        None,
    )
    try:
        ts = pywintypes.Time(when)
        win32file.SetFileTime(handle, ts, None, None)
    finally:
        handle.Close()
