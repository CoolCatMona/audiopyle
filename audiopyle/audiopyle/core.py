from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
import json
from typing import Self


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

    @property
    def __dict__(self) -> dict:
        """Dictionary representation of the File object."""
        return asdict(self)

    @property
    def json(self) -> str:
        """JSON Representation of File object."""
        return json.dumps(self.__dict__)

    def move(self, new_filepath: str):
        """Moves the file to a new filepath."""
        # Move File
        # Update Filepath
        # TODO: How do I keep track of the original file and where to move it?
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def _from_filepath(cls) -> Self:
        """Creates a File object given a filepath."""
        pass
