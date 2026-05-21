"""Base ``File`` dataclass used by audio and rekordbox modules."""

from __future__ import annotations

import json
import shutil
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Self

from audiopyle.timestamps import get_creation_time, get_mtime, set_creation_time, set_mtime

MONTH_DIR: dict[int, str] = {
    1: "01 - January",
    2: "02 - February",
    3: "03 - March",
    4: "04 - April",
    5: "05 - May",
    6: "06 - June",
    7: "07 - July",
    8: "08 - August",
    9: "09 - September",
    10: "10 - October",
    11: "11 - November",
    12: "12 - December",
}


@dataclass
class File(ABC):
    """Representation of a local file and its date-bucket metadata.

    Attributes:
        filename: The basename of the file.
        filepath: The full path to the file as a string. Stored as a string
            for JSON-friendliness.
        download_year: Four-digit string year of the file's relevant date.
        download_month: ``MM - Monthname`` string for the file's month.
    """

    filename: str
    filepath: str
    download_year: str = field(default="")
    download_month: str = field(default="")

    def to_dict(self) -> dict[str, object]:
        """Return a plain-dict representation, safe for JSON dumping."""
        return asdict(self)

    @property
    def json(self) -> str:
        """Return a JSON-encoded string of :meth:`to_dict`."""
        return json.dumps(self.to_dict())

    def move(self, target_directory: str | Path) -> None:
        """Move this file into ``target_directory``, preserving timestamps.

        Args:
            target_directory: Destination directory. Created if missing.
        """
        target_directory = Path(target_directory)
        source = Path(self.filepath)
        if not source.is_file():
            return

        target_directory.mkdir(parents=True, exist_ok=True)
        target = target_directory / source.name

        if source.resolve() == target.resolve():
            return

        creation = get_creation_time(source)
        mtime = get_mtime(source)

        shutil.copy2(source, target)
        set_mtime(target, mtime)
        set_creation_time(target, creation)

        source.unlink()
        if not any(source.parent.iterdir()):
            source.parent.rmdir()

        self.filepath = str(target.resolve())

    @staticmethod
    def date_components(filepath: str | Path) -> tuple[datetime, str, str]:
        """Return the file's mtime plus its formatted year and month-dir.

        Args:
            filepath: Path to inspect.

        Returns:
            Tuple of (mtime as ``datetime``, ``YYYY`` string,
            ``MM - Monthname`` string).
        """
        when = get_mtime(Path(filepath))
        return when, f"{when.year:04d}", MONTH_DIR[when.month]

    @classmethod
    @abstractmethod
    def _from_filepath(cls, filepath: str | Path) -> Self:
        """Construct an instance of this class from a filesystem path."""
