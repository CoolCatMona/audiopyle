import json
import shutil
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Self

from audiopyle.builtins import get_creation_time, set_creation_time

DATE: dict = {
    "01": "01 - January",
    "02": "02 - February",
    "03": "03 - March",
    "04": "04 - April",
    "05": "05 - May",
    "06": "06 - June",
    "07": "07 - July",
    "08": "08 - August",
    "09": "09 - September",
    "10": "10 - October",
    "11": "11 - November",
    "12": "12 - December",
}


@dataclass
class File(ABC):
    """
    Representation of a of a local file and its metadata.

    Args:
        _filename (str): Name of the file.
        _filepath (str): Path to the file.
    """

    _filename: str
    _filepath: str
    _download_year: str
    _download_month: str

    @property
    def __dict__(self) -> dict:
        """Dictionary representation of the File object."""
        return asdict(self)

    @property
    def json(self) -> str:
        """JSON Representation of File object."""
        return json.dumps(self.__dict__)

    def move(self, target_directory: str | Path) -> None:
        """Moves the file to a new filepath."""
        if isinstance(target_directory, str):
            target_directory = Path(target_directory)

        source = Path(self._filepath)
        if not source.is_file():
            print(f"{source.name} does not exist!")
            return

        # TODO: Handle Images (Move them with the album)
        if source.suffix in [".jpg", ".png"]:
            source.unlink()
            # Remove the source directory if it's empty
            if not any(source.parent.iterdir()):
                source.parent.rmdir()

            return

        target = target_directory / source.name

        if source.resolve() == target.resolve():
            return

        # Get the creation time of the source file
        creation_time = get_creation_time(str(source))

        target.parent.mkdir(parents=True, exist_ok=True)

        try:
            shutil.copy2(source, target)
        except FileNotFoundError:
            print(f"Error moving {source.name}")
            return

        # Set the creation time on the destination file
        set_creation_time(str(target), creation_time)

        source.unlink()

        # Remove the source directory if it's empty
        if not any(source.parent.iterdir()):
            source.parent.rmdir()

        self._filepath = target.resolve()

    @classmethod
    @abstractmethod
    def _from_filepath(cls) -> Self:
        """Creates a File object given a filepath."""
        pass
