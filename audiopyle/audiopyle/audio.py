from audiopyle.core import File
from typing import Self
from pathlib import Path

# from pydub.utils import mediainfo


class Audio(File):
    """Representation of an Audio File."""

    title: str
    album: str
    year: int
    length: int
    bit_rate: int

    tags: list[str]

    @classmethod
    def _from_filepath(cls, filepath: Path | str) -> Self:
        """Creates an Audio object given a filepath."""
        if isinstance(filepath, Path):
            filename = filepath.name
            filepath = filepath.resolve()
        else:
            filename = Path(filepath).name
        return cls(_filepath=filepath, _filename=filename)


def get_audio_oirigin(comment: str) -> str:
    """Reads the comment metadata of a file to determine its origin i.e bandcamp, beatport, etc."""
    raise NotImplementedError
