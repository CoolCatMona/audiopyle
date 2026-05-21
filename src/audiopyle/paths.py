"""Compute target paths and plan conflict-aware moves into the library tree."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from audiopyle.core import MONTH_DIR


def format_year_month(when: datetime) -> tuple[str, str]:
    """Return ``(YYYY, "MM - Monthname")`` strings for ``when``.

    Args:
        when: A naive ``datetime`` whose year/month determine the bucket.

    Returns:
        Tuple of (four-digit year, ``MM - Monthname`` directory name).
    """
    return f"{when.year:04d}", MONTH_DIR[when.month]


def compute_album_target(library: Path, when: datetime, zip_stem: str) -> Path:
    """Return ``library/YYYY/MM - Monthname/<zip_stem>``."""
    year, month = format_year_month(when)
    return library / year / month / zip_stem


def compute_single_target(library: Path, when: datetime, filename: str) -> Path:
    """Return ``library/YYYY/MM - Monthname/<filename>``."""
    year, month = format_year_month(when)
    return library / year / month / filename


def plan_merge(
    source_files: list[Path], target_dir: Path
) -> tuple[list[tuple[Path, Path]], list[Path]]:
    """Compute which source files can move into ``target_dir`` and which collide.

    Args:
        source_files: Files staged for the move.
        target_dir: Destination directory (may or may not exist).

    Returns:
        Tuple of ``(moves, skipped)`` where ``moves`` is a list of
        ``(source, target)`` pairs and ``skipped`` lists sources whose
        target name already exists.
    """
    moves: list[tuple[Path, Path]] = []
    skipped: list[Path] = []
    for source in source_files:
        candidate = target_dir / source.name
        if candidate.exists():
            skipped.append(source)
        else:
            moves.append((source, candidate))
    return moves, skipped
