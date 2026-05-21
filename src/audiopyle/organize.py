"""Staging-to-library pipeline.

The pipeline runs in four stages: :func:`scan_staging` lists candidate
items, :func:`classify` decides what each is, :func:`plan_action` figures
out where it goes, and :func:`execute` performs the moves (or describes
them under ``--dry-run``).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from pathlib import Path

from audiopyle.builtins import DEFAULT_AUDIO_EXTENSIONS, is_audio
from audiopyle.timestamps import get_mtime

logger = logging.getLogger(__name__)


class ItemKind(StrEnum):
    """The classification of one staged item."""

    ALBUM_ARCHIVE = "album_archive"
    SINGLE_FILE = "single_file"
    IGNORED = "ignored"


@dataclass(frozen=True)
class StagedItem:
    """One thing at the top level of the staging directory."""

    source: Path
    is_archive: bool
    mtime: datetime


def scan_staging(
    staging: Path, audio_extensions: tuple[str, ...] = DEFAULT_AUDIO_EXTENSIONS
) -> list[StagedItem]:
    """Return the candidate items at the top of ``staging``.

    Args:
        staging: The staging directory to scan.
        audio_extensions: Suffixes that count as audio.

    Returns:
        A deterministic list of :class:`StagedItem`. Hidden files and
        top-level subdirectories are skipped; subdirectories generate a
        warning log.
    """
    if not staging.exists():
        return []

    items: list[StagedItem] = []
    for entry in sorted(staging.iterdir()):
        name = entry.name
        if name.startswith("."):
            continue
        if entry.is_dir():
            logger.warning("Skipping top-level directory: %s", entry)
            continue
        suffix = entry.suffix.lower()
        if suffix == ".zip":
            items.append(StagedItem(source=entry, is_archive=True, mtime=get_mtime(entry)))
        elif is_audio(entry, audio_extensions):
            items.append(StagedItem(source=entry, is_archive=False, mtime=get_mtime(entry)))
        else:
            logger.warning("Skipping unrecognized file: %s", entry)
    return items
