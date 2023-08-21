from audiopyle.core import File
from typing import Self
from pydub.utils import mediainfo


class Audio(File):
    """Representation of an Audio File."""

    title: str
    album: str
    year: int
    length: int
    bit_rate: int

    tags: list[str]

    @classmethod
    def _from_filepath(cls, filepath: str) -> Self:
        raise NotImplementedError


def get_audio_oirigin(comment: str) -> str:
    """Reads the comment metadata of a file to determine its origin i.e bandcamp, beatport, etc."""
    raise NotImplementedError
