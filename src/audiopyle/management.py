"""File and directory management utilities."""

from __future__ import annotations

import os
import shutil
from functools import cached_property
from pathlib import Path
from typing import Self

from audiopyle import builtins


class Directory:
    """A read-side view of a directory of files."""

    def __init__(self, directory_path: Path) -> None:
        """Initialize from a path that is known to exist and be a directory."""
        self.logger = builtins.get_or_configure_logger(__name__)
        self.directory_path: Path = directory_path
        self._directory_path_str: str = str(self.directory_path)
        self._directory_size: int = os.path.getsize(self.directory_path)
        self._num_files: int = builtins.count_files(self.directory_path)

    @classmethod
    def _from_filepath(cls, directory_path: str | Path) -> Self:
        """Construct a :class:`Directory` after validating the path."""
        builtins.ensure_exists(directory_path)
        builtins.ensure_directory(directory_path)
        return cls(Path(directory_path))

    @cached_property
    def files(self) -> list[Path]:
        """Return all files under :attr:`directory_path` as paths.

        This is intentionally lazy: it does not parse audio metadata. Use
        :meth:`audio_files` when ID3/tag reads are actually needed.
        """
        result: list[Path] = []
        for root, _, files in os.walk(self.directory_path):
            for name in files:
                result.append(Path(root) / name)
        return result

    def audio_files(self) -> list[Path]:
        """Return only files whose suffix is in the default audio set."""
        return [p for p in self.files if builtins.is_audio(p)]

    @cached_property
    def empty_subdirectories(self) -> list[Path]:
        """Return all empty subdirectories (excluding the root)."""
        return [
            subdir
            for subdir in self.directory_path.rglob("*")
            if subdir.is_dir() and not any(subdir.iterdir())
        ]

    def delete_empty_subdirectories(self) -> None:
        """Delete every empty subdirectory found by :attr:`empty_subdirectories`."""
        for subdir in self.empty_subdirectories:
            subdir.rmdir()

    def _create_directory(self, *subdirectories: str) -> Path:
        """Create and return a nested subdirectory under the managed path."""
        new_path = Path(self.directory_path, *subdirectories)
        new_path.mkdir(parents=True, exist_ok=True)
        return new_path

    def backup(self) -> Path:
        """Copy the directory to a sibling ``<name>_bak`` location.

        Returns:
            The backup directory's path.
        """
        self.logger.debug(
            "Creating backup of %s (%d files, %d bytes)",
            self.directory_path,
            self._num_files,
            self._directory_size,
        )
        backup_path = Path(self._directory_path_str + "_bak")
        shutil.copytree(self.directory_path, backup_path)
        return backup_path

    def move_files(self) -> None:
        """Reserved for future use.

        The actual staging-to-library move logic lives in
        :mod:`audiopyle.organize`. This method exists as a marker on
        legacy callers; invoke :func:`audiopyle.organize.organize` instead.
        """
        raise NotImplementedError("Use audiopyle.organize.organize instead.")
