"""File and Directory management."""
from typing import Self
from audiopyle import builtins
from pathlib import Path
import os
import shutil


class Directory:
    """Class for managing a directory of files."""

    def __init__(self, directory_path: Path):
        # TODO: This Class should store the information for subdirectories as well, but how to associate an old directory structure with a new directory structure?
        self.logger = builtins.get_or_configure_logger(__name__)
        self.directory_path: Path = directory_path
        self._directory_path_str = str(self.directory_path)
        self._directory_size: int = os.path.getsize(self.directory_path)
        self._num_files: int = builtins.count_files(self.directory_path)

    def backup(self):
        """Creates a backup of a directory"""
        self.logger.debug(
            f"Creating backup of {self.directory_path} ({self._num_files} totaling {self._directory_size} bytes)..."
        )
        backup_filepath = self._directory_path_str + "_bak"
        shutil.copytree(self.directory_path, backup_filepath)
        self.logger.debug(f"Backup created at {backup_filepath}")

    @classmethod
    def _from_filepath(cls, directory_path: str) -> Self:
        """Creates a Directory object given a filepath."""
        builtins.ensure_exists(directory_path)
        builtins.ensure_directory(directory_path)
        return cls(directory_path)

    def sort(self):
        """Sorts files in a directory"""
        pass
