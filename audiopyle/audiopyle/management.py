"""File and Directory management."""

import os
import shutil
from functools import cached_property
from pathlib import Path
from typing import Self

from audiopyle import audio, builtins, core


class Directory:
    """Class for managing a directory of files."""

    def __init__(self, directory_path: Path):
        self.logger = builtins.get_or_configure_logger(__name__)
        self.directory_path: Path = directory_path
        self._directory_path_str = str(self.directory_path)
        self._directory_size: int = os.path.getsize(self.directory_path)
        self._num_files: int = builtins.count_files(self.directory_path)

    @classmethod
    def _from_filepath(cls, directory_path: str) -> Self:
        """Creates a Directory object given a filepath."""
        builtins.ensure_exists(directory_path)
        builtins.ensure_directory(directory_path)
        return cls(directory_path)

    @cached_property
    def files(self) -> list[core.File]:
        """Recursively walk directories for a list of file objects"""
        all_files = []
        for root, _, files in os.walk(self.directory_path):
            for _file in files:
                # TODO: Create file based on file extension
                all_files.append(audio.Audio._from_filepath(Path(root, _file)))
        return all_files

    @cached_property
    def _empty_directories(self) -> list[Path]:
        """Returns a list of empty subdirectories."""
        dirs = []
        for subdir in self.directory_path.rglob("*"):
            if subdir.is_dir() and not any(subdir.iterdir()):
                dirs.append(subdir)
        return dirs

    def _delete_empty_directories(self):
        """Deletes empty subdirectories via ``pathlib.Path.rmdir()``."""
        for directory in self._empty_directories:
            directory.rmdir()

    def _create_directory(self, *subdirectories: str) -> Path:
        """Creates a new subdirectory."""
        _new_path = Path(self.directory_path, *subdirectories)
        _new_path.mkdir(parents=True, exist_ok=True)
        return _new_path

    def backup(self):
        """Creates a backup of a directory"""
        self.logger.debug(
            f"Creating backup of {self.directory_path} ({self._num_files} totaling {self._directory_size} bytes)..."
        )
        backup_filepath = self._directory_path_str + "_bak"
        shutil.copytree(self.directory_path, backup_filepath)
        self.logger.debug(f"Backup created at {backup_filepath}")

    def move_files(self):
        """Move files in a directory"""
        # For each file in directory
        # use some criteria to move it to a new directory, i.e 'Root / Year / Album /' or 'Root / Genre / Album /'
        # Handle one or more of the criteria not existing
        # target_directory = self._create_directory(file.year, file.album)
        # file.move(target_directory)
        # Remove empty directories afterwards
        # Should be able to do this multithreaded...
        raise NotImplementedError
