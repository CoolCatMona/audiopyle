"""Safe zip extraction with zip-slip guards and top-level folder flattening."""

from __future__ import annotations

import os
import zipfile
from pathlib import Path, PurePosixPath

from audiopyle.exceptions import ExtractionError


def count_audio_in_zip(zip_path: Path, audio_extensions: tuple[str, ...]) -> int:
    """Return how many recognized audio files live inside ``zip_path``.

    Args:
        zip_path: Path to the zip archive.
        audio_extensions: Suffixes that count as audio (with leading dot,
            lower-case).

    Returns:
        Number of members whose lower-case suffix is in ``audio_extensions``.
    """
    exts = {ext.lower() for ext in audio_extensions}
    with zipfile.ZipFile(zip_path) as zf:
        return sum(1 for name in zf.namelist() if not name.endswith("/") and _suffix(name) in exts)


def extract_zip(
    zip_path: Path, dest_dir: Path, audio_extensions: tuple[str, ...]
) -> tuple[list[Path], list[Path]]:
    """Extract ``zip_path`` into ``dest_dir`` and return (audio, extras).

    If every member is nested inside a single top-level folder, that folder
    is stripped during extraction so the destination does not get a
    redundant outer directory.

    Args:
        zip_path: Archive to extract.
        dest_dir: Destination directory (created if missing).
        audio_extensions: Suffixes that classify a member as audio.

    Returns:
        Tuple of (audio paths, extra paths) under ``dest_dir``.

    Raises:
        ExtractionError: If any member uses an absolute path or contains
            ``..`` segments.
    """
    dest_dir.mkdir(parents=True, exist_ok=True)
    audio_paths: list[Path] = []
    extras: list[Path] = []
    exts = {ext.lower() for ext in audio_extensions}

    with zipfile.ZipFile(zip_path) as zf:
        members = [name for name in zf.namelist() if not name.endswith("/")]
        strip_prefix = _common_top_level(members)

        for member in members:
            relative = member[len(strip_prefix) :] if strip_prefix else member
            _validate_member(member, relative)
            target = dest_dir / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(member) as src, open(target, "wb") as out:
                out.write(src.read())
            (audio_paths if _suffix(relative) in exts else extras).append(target)

    return audio_paths, extras


def _suffix(name: str) -> str:
    return os.path.splitext(name)[1].lower()


def _common_top_level(members: list[str]) -> str:
    """Return the single shared top-level folder name (with trailing slash) or ''."""
    if not members:
        return ""
    first = PurePosixPath(members[0]).parts
    if not first:
        return ""
    candidate = first[0]
    for name in members:
        parts = PurePosixPath(name).parts
        if not parts or parts[0] != candidate or len(parts) < 2:
            return ""
    return candidate + "/"


def _validate_member(original: str, relative: str) -> None:
    if PurePosixPath(original).is_absolute() or original.startswith("/") or "\\" in original:
        raise ExtractionError(f"Unsafe archive member (absolute path): {original!r}")
    if ".." in PurePosixPath(relative).parts:
        raise ExtractionError(f"Unsafe archive member (path traversal): {original!r}")
