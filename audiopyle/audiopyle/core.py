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

    @classmethod
    @abstractmethod
    def _from_filepath(cls) -> Self:
        """Creates a File object given a filepath."""
        pass
