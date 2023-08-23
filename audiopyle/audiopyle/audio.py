from audiopyle.core import File
from typing import Self
from pathlib import Path
from dataclasses import dataclass

from pydub.utils import mediainfo


@dataclass
class Audio(File):
    """Representation of an Audio File."""

    title: str
    album: str
    year: int
    length: int
    comment: str
    bit_rate: int

    tags: list[str] = None

    @classmethod
    def _from_filepath(cls, filepath: Path | str) -> Self:
        """Creates an Audio object given a filepath."""
        if isinstance(filepath, Path):
            filename = filepath.name
            filepath = filepath.resolve()
        else:
            filename = Path(filepath).name

        try:
            file_info = mediainfo(filepath)
            tags = file_info.get("TAG")
            title = tags.get("title", "N/A")
            album = tags.get("album", "N/A")
            year = tags.get("date", "N/A")
            comment = tags.get("comment", "") + tags.get("ID3v1 Comment", "")

            length = file_info.get("duration", 0)
            bit_rate = file_info.get("bit_rate", 0)

        except AttributeError as e:
            raise

        return cls(
            _filepath=filepath,
            _filename=filename,
            title=title,
            album=album,
            year=year,
            length=length,
            bit_rate=bit_rate,
            comment=comment,
        )


def get_audio_oirigin(comment: str) -> str:
    """Reads the comment metadata of a file to determine its origin i.e bandcamp, beatport, etc."""
    raise NotImplementedError
