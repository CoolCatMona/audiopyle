"""Tests for safe zip extraction."""

from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

from audiopyle import extract
from audiopyle.exceptions import ExtractionError


def _make_zip(path: Path, members: dict[str, bytes]) -> None:
    with zipfile.ZipFile(path, "w") as zf:
        for name, content in members.items():
            zf.writestr(name, content)


def test_count_audio_in_zip(tmp_path: Path) -> None:
    archive = tmp_path / "album.zip"
    _make_zip(
        archive,
        {
            "01 - track.mp3": b"",
            "02 - track.flac": b"",
            "cover.jpg": b"",
        },
    )

    count = extract.count_audio_in_zip(archive, (".mp3", ".flac", ".wav", ".aiff"))

    assert count == 2


def test_extract_zip_returns_audio_and_extras(tmp_path: Path) -> None:
    archive = tmp_path / "album.zip"
    _make_zip(
        archive,
        {
            "01 - track.mp3": b"a",
            "cover.jpg": b"b",
            "notes.txt": b"c",
        },
    )

    dest = tmp_path / "out"
    audio, extras = extract.extract_zip(archive, dest, (".mp3",))

    assert {p.name for p in audio} == {"01 - track.mp3"}
    assert {p.name for p in extras} == {"cover.jpg", "notes.txt"}
    assert (dest / "01 - track.mp3").read_bytes() == b"a"


def test_extract_zip_strips_single_top_level_folder(tmp_path: Path) -> None:
    archive = tmp_path / "album.zip"
    _make_zip(
        archive,
        {
            "Album Title/01 - track.mp3": b"a",
            "Album Title/02 - track.mp3": b"b",
            "Album Title/cover.jpg": b"c",
        },
    )

    dest = tmp_path / "out"
    audio, _extras = extract.extract_zip(archive, dest, (".mp3",))

    assert {p.name for p in audio} == {"01 - track.mp3", "02 - track.mp3"}
    assert (dest / "01 - track.mp3").exists()
    assert (dest / "cover.jpg").exists()


def test_extract_zip_rejects_zip_slip(tmp_path: Path) -> None:
    archive = tmp_path / "evil.zip"
    _make_zip(archive, {"../../../etc/passwd": b"oops"})

    with pytest.raises(ExtractionError):
        extract.extract_zip(archive, tmp_path / "out", (".mp3",))


def test_extract_zip_rejects_absolute_member(tmp_path: Path) -> None:
    archive = tmp_path / "evil.zip"
    _make_zip(archive, {"/etc/passwd": b"oops"})

    with pytest.raises(ExtractionError):
        extract.extract_zip(archive, tmp_path / "out", (".mp3",))
