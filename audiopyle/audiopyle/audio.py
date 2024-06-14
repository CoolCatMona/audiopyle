import os
import re
import time
import urllib.parse
from dataclasses import dataclass, field
from pathlib import Path
from typing import Self

from pydub.utils import mediainfo

from audiopyle.core import DATE, File

CURRENT_ALBUMS: dict = {}


@dataclass
class Audio(File):
    """Representation of an Audio File."""

    title: str
    album: str
    artist: str
    album_artist: str
    year: int
    length: int
    comment: str
    origin: str
    bit_rate: int
    _rekordbox_uri: str

    tags: list[str] = field(default_factory=list)

    @classmethod
    def _from_filepath(cls, filepath: Path | str) -> Self:
        """Creates an Audio object given a filepath."""
        if isinstance(filepath, Path):
            filename = filepath.name
            filepath = str(filepath.resolve())
        else:
            filename = str(Path(filepath).name)

        try:
            file_info = mediainfo(filepath)
            _rekordbox_uri = filepath_to_rekordbox_uri(filepath)
            tags = file_info.get("TAG", {})
            title = tags.get("title", "No Title")
            album = tags.get("album", title)

            CURRENT_ALBUMS[album] = CURRENT_ALBUMS.get(album, {album: {}})

            artist = tags.get("artist", "Unknown Artist")
            _album_artist = tags.get("album_artist", artist)
            album_artist = handle_artist(album, _album_artist)

            year = tags.get("date", "N/A")
            comment = tags.get("comment", "") or tags.get("ID3v1 Comment", "")

            origin = get_audio_oirigin(comment)

            length = file_info.get("duration", 0)
            bit_rate = file_info.get("bit_rate", 0)

            # TODO: Assign single date per album, if this is part of an album
            _download_date = time.strptime(time.ctime(os.path.getctime(filepath)))
            download_year = time.strftime("%Y", _download_date)
            download_month = DATE.get(time.strftime("%m", _download_date))

            download_year, download_month = get_album_date_if_exists(
                album, download_year, download_month
            )

        except AttributeError as e:
            raise

        return cls(
            _filepath=filepath,
            _filename=filename,
            _download_year=download_year,
            _download_month=download_month,
            title=title,
            album=album,
            artist=artist,
            album_artist=album_artist,
            year=year,
            length=length,
            bit_rate=bit_rate,
            comment=comment,
            origin=origin,
            _rekordbox_uri=_rekordbox_uri,
        )


def get_audio_oirigin(comment: str) -> str:
    """Reads the comment metadata of a file to determine its origin i.e bandcamp, beatport, etc."""
    if "bandcamp.com" in comment:
        bandcamp_regex = r"https?://[^\s]+"
        origin = re.findall(bandcamp_regex, comment)[0]
    else:
        origin = "other"

    return origin


def get_album_date_if_exists(album: str, year: str, month: str):
    CURRENT_ALBUMS[album]["year"] = CURRENT_ALBUMS[album].get("year", year)
    CURRENT_ALBUMS[album]["month"] = CURRENT_ALBUMS[album].get("month", month)
    return CURRENT_ALBUMS[album]["year"], CURRENT_ALBUMS[album]["month"]


def handle_artist(album: str, artist: str):
    existing_artist = CURRENT_ALBUMS[album].get("artist")
    if artist == existing_artist:
        pass
    elif existing_artist == None:
        CURRENT_ALBUMS[album]["artist"] = artist
    else:
        CURRENT_ALBUMS[album]["artist"] = "Various Artists"

    return CURRENT_ALBUMS[album]["artist"]


def filepath_to_rekordbox_uri(filepath: str) -> str:
    rekordbox_uri = "file://localhost/" + urllib.parse.quote(
        filepath, safe=":\()!,+$#@"
    ).replace("\\", "/")

    # Convert percent-encoded sequences to lowercase
    rekordbox_uri = re.sub(
        r"%[0-9A-Fa-f]{2}", lambda x: x.group(0).lower(), rekordbox_uri
    )

    return rekordbox_uri
