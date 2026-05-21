"""Audio file representation backed by pydub mediainfo reads."""

from __future__ import annotations

import re
import urllib.parse
from dataclasses import dataclass, field
from pathlib import Path
from typing import Self

from pydub.utils import mediainfo

from audiopyle.core import File


@dataclass
class AlbumState:
    """Aggregate state for a single album across its tracks.

    The pipeline reads tracks one at a time. To make album-level decisions
    (a unified date, a single album artist, etc.) we accumulate state per
    album in this dataclass instead of a module-level dict.
    """

    artist: str | None = None
    album_artist: str | None = None
    year: str | None = None
    month: str | None = None

    def merge_artist(self, candidate: str) -> str:
        """Return the album-level artist after considering ``candidate``.

        If we have not seen an artist yet, ``candidate`` wins. If the
        existing artist matches ``candidate``, nothing changes. Otherwise
        the artist becomes "Various Artists".
        """
        if self.artist is None:
            self.artist = candidate
        elif self.artist != candidate:
            self.artist = "Various Artists"
        return self.artist


class AlbumRegistry:
    """A keyed collection of :class:`AlbumState` entries.

    A new instance should be created per pipeline run so test order does
    not leak state between cases.
    """

    def __init__(self) -> None:
        self._by_album: dict[str, AlbumState] = {}

    def get(self, album: str) -> AlbumState:
        """Return the :class:`AlbumState` for ``album`` (creating it lazily)."""
        if album not in self._by_album:
            self._by_album[album] = AlbumState()
        return self._by_album[album]


@dataclass
class Audio(File):
    """Representation of an audio file with selected metadata."""

    title: str = ""
    album: str = ""
    artist: str = ""
    album_artist: str = ""
    year: str = "N/A"
    length: float = 0.0
    comment: str = ""
    origin: str = "other"
    bit_rate: int = 0
    rekordbox_uri: str = ""
    tags: list[str] = field(default_factory=list)

    @classmethod
    def _from_filepath(
        cls,
        filepath: str | Path,
        registry: AlbumRegistry | None = None,
    ) -> Self:
        """Construct an :class:`Audio` instance from a filesystem path.

        Args:
            filepath: Path to the audio file.
            registry: Optional :class:`AlbumRegistry`. If omitted a fresh
                registry is used (album-level aggregation is then per-call).

        Returns:
            A populated :class:`Audio` dataclass.
        """
        registry = registry or AlbumRegistry()
        path = Path(filepath)
        filepath_str = str(path.resolve())

        info = mediainfo(filepath_str)
        tags = info.get("TAG", {}) or {}

        title = tags.get("title", "No Title")
        album = tags.get("album", title)
        artist = tags.get("artist", "Unknown Artist")
        album_artist_raw = tags.get("album_artist", artist)
        comment = tags.get("comment", "") or tags.get("ID3v1 Comment", "")

        state = registry.get(album)
        merged_artist = state.merge_artist(album_artist_raw)

        _, year, month = File.date_components(path)
        if state.year is None:
            state.year = year
        if state.month is None:
            state.month = month

        return cls(
            filename=path.name,
            filepath=filepath_str,
            download_year=state.year,
            download_month=state.month,
            title=title,
            album=album,
            artist=artist,
            album_artist=merged_artist,
            year=tags.get("date", "N/A"),
            length=float(info.get("duration", 0) or 0),
            bit_rate=int(info.get("bit_rate", 0) or 0),
            comment=comment,
            origin=get_audio_origin(comment),
            rekordbox_uri=filepath_to_rekordbox_uri(filepath_str),
        )


def get_audio_origin(comment: str) -> str:
    """Return a best-guess origin URL for a track based on its comment tag.

    Args:
        comment: The track's comment metadata.

    Returns:
        The first bandcamp URL found in the comment, or ``"other"``.
    """
    if "bandcamp.com" in comment:
        match = re.search(r"https?://\S+", comment)
        if match:
            return match.group(0)
    return "other"


def filepath_to_rekordbox_uri(filepath: str) -> str:
    """Return a ``file://localhost/`` URI compatible with Rekordbox XML.

    Args:
        filepath: A filesystem path to encode.

    Returns:
        A URI string with percent-encoded sequences lower-cased to match
        Rekordbox's own normalization.
    """
    forward = filepath.replace("\\", "/")
    encoded = urllib.parse.quote(forward, safe="/:()!,+$#@'")
    uri = "file://localhost/" + encoded
    return re.sub(r"%[0-9A-Fa-f]{2}", lambda m: m.group(0).lower(), uri)
