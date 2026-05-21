"""Staging-to-library pipeline.

The pipeline runs in four stages: :func:`scan_staging` lists candidate
items, :func:`classify` decides what each is, :func:`plan_action` figures
out where it goes, and :func:`execute` performs the moves (or describes
them under ``--dry-run``).
"""

from __future__ import annotations

import logging
import shutil
import tempfile
import zipfile
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from pathlib import Path

from audiopyle.builtins import DEFAULT_AUDIO_EXTENSIONS, is_audio
from audiopyle.extract import count_audio_in_zip, extract_zip
from audiopyle.paths import compute_album_target, compute_single_target, plan_merge
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


def classify(item: StagedItem, audio_extensions: tuple[str, ...]) -> ItemKind:
    """Decide whether an item is an album archive, a single, or ignored.

    Args:
        item: One :class:`StagedItem` from :func:`scan_staging`.
        audio_extensions: Suffixes that classify a member as audio.

    Returns:
        One of :class:`ItemKind`.
    """
    if item.is_archive:
        audio_count = count_audio_in_zip(item.source, audio_extensions)
        if audio_count >= 2:
            return ItemKind.ALBUM_ARCHIVE
        if audio_count == 1:
            return ItemKind.SINGLE_FILE
        return ItemKind.IGNORED
    return ItemKind.SINGLE_FILE


@dataclass
class Action:
    """One planned operation against staging + library."""

    kind: ItemKind
    item: StagedItem
    target: Path
    audio_files: list[Path] = field(default_factory=list)
    extras: list[Path] = field(default_factory=list)

    def describe(self) -> str:
        """Return a one-line description suitable for ``--dry-run`` output."""
        if self.kind is ItemKind.ALBUM_ARCHIVE:
            return f"album: {self.item.source.name} -> {self.target}"
        if self.kind is ItemKind.SINGLE_FILE:
            return f"single: {self.item.source.name} -> {self.target}"
        return f"ignored: {self.item.source.name}"


@dataclass
class ActionResult:
    """The outcome of executing one :class:`Action`.

    There is one ``ActionResult`` per planned action (not per file). For
    album archives, ``files_moved`` / ``files_skipped`` capture how many
    individual tracks went into the target and how many collided with an
    existing name.
    """

    kind: ItemKind
    source: Path
    target: Path
    ok: bool
    files_moved: int = 0
    files_skipped: int = 0
    reason: str = ""


def organize(
    staging: Path,
    library: Path,
    audio_extensions: tuple[str, ...] = DEFAULT_AUDIO_EXTENSIONS,
    dry_run: bool = False,
) -> list[ActionResult]:
    """End-to-end pipeline: scan -> classify -> plan -> execute.

    Args:
        staging: The staging directory to drain.
        library: The library root the items should land under.
        audio_extensions: Suffixes that classify a file as audio.
        dry_run: When ``True``, log the plan but do not touch disk.

    Returns:
        One :class:`ActionResult` per planned action.
    """
    library.mkdir(parents=True, exist_ok=True)
    results: list[ActionResult] = []

    for item in scan_staging(staging, audio_extensions):
        kind = classify(item, audio_extensions)
        if kind is ItemKind.IGNORED:
            logger.warning("Ignored: %s", item.source)
            results.append(
                ActionResult(
                    kind=ItemKind.IGNORED,
                    source=item.source,
                    target=item.source,
                    ok=False,
                    reason="ignored",
                )
            )
            continue

        target = _target_for(item, kind, library, audio_extensions)
        action = Action(kind=kind, item=item, target=target)
        logger.info(action.describe())

        if dry_run:
            results.append(
                ActionResult(
                    kind=kind,
                    source=item.source,
                    target=target,
                    ok=True,
                    reason="dry-run",
                )
            )
            continue

        results.append(_execute(action, audio_extensions))

    if not dry_run:
        _delete_empty_subdirectories(staging)

    return results


def _target_for(
    item: StagedItem, kind: ItemKind, library: Path, audio_extensions: tuple[str, ...]
) -> Path:
    """Compute the destination path for ``item``."""
    if kind is ItemKind.ALBUM_ARCHIVE:
        return compute_album_target(library, item.mtime, item.source.stem)
    if item.is_archive:
        track_name = _peek_single_track_name(item.source, audio_extensions)
        return compute_single_target(library, item.mtime, track_name)
    return compute_single_target(library, item.mtime, item.source.name)


def _peek_single_track_name(zip_path: Path, audio_extensions: tuple[str, ...]) -> str:
    """Return the basename of the single audio member inside ``zip_path``."""
    exts = {ext.lower() for ext in audio_extensions}
    with zipfile.ZipFile(zip_path) as zf:
        for name in zf.namelist():
            if name.endswith("/"):
                continue
            suffix = Path(name).suffix.lower()
            if suffix in exts:
                return Path(name).name
    return zip_path.stem


def _execute(action: Action, audio_extensions: tuple[str, ...]) -> ActionResult:
    if action.kind is ItemKind.ALBUM_ARCHIVE:
        return _execute_album(action, audio_extensions)
    return _execute_single(action, audio_extensions)


def _execute_album(action: Action, audio_extensions: tuple[str, ...]) -> ActionResult:
    action.target.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        audio, extras = extract_zip(action.item.source, tmp_path, audio_extensions)
        moves, skipped = plan_merge(audio + extras, action.target)
        for source, target in moves:
            shutil.move(str(source), str(target))

    action.item.source.unlink()
    return ActionResult(
        kind=ItemKind.ALBUM_ARCHIVE,
        source=action.item.source,
        target=action.target,
        ok=True,
        files_moved=len(moves),
        files_skipped=len(skipped),
        reason="duplicate name" if skipped else "",
    )


def _execute_single(action: Action, audio_extensions: tuple[str, ...]) -> ActionResult:
    action.target.parent.mkdir(parents=True, exist_ok=True)
    if action.target.exists():
        return ActionResult(
            kind=ItemKind.SINGLE_FILE,
            source=action.item.source,
            target=action.target,
            ok=False,
            files_skipped=1,
            reason="duplicate name",
        )

    if action.item.is_archive:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            audio, _ = extract_zip(action.item.source, tmp_path, audio_extensions)
            if not audio:
                return ActionResult(
                    kind=ItemKind.SINGLE_FILE,
                    source=action.item.source,
                    target=action.target,
                    ok=False,
                    reason="no audio in archive",
                )
            shutil.move(str(audio[0]), str(action.target))
        action.item.source.unlink()
    else:
        shutil.move(str(action.item.source), str(action.target))

    return ActionResult(
        kind=ItemKind.SINGLE_FILE,
        source=action.item.source,
        target=action.target,
        ok=True,
        files_moved=1,
    )


def _delete_empty_subdirectories(root: Path) -> None:
    for subdir in sorted(root.rglob("*"), reverse=True):
        if subdir.is_dir() and not any(subdir.iterdir()):
            subdir.rmdir()
