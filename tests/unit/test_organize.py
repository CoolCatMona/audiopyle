"""Tests for the staging-to-library organize pipeline."""

from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

from audiopyle import organize


def _make_zip(path: Path, members: dict[str, bytes]) -> None:
    with zipfile.ZipFile(path, "w") as zf:
        for name, content in members.items():
            zf.writestr(name, content)


@pytest.fixture
def staging_with_mixed_items(tmp_path: Path) -> Path:
    """A staging directory containing one album zip and one loose single."""
    staging = tmp_path / "staging"
    staging.mkdir()

    album = staging / "Artist - Album.zip"
    _make_zip(album, {"01 - track.mp3": b"a", "02 - track.mp3": b"b"})

    single = staging / "loose-track.mp3"
    single.write_bytes(b"single")

    (staging / ".hidden").write_text("ignored")

    return staging


def test_scan_finds_top_level_archives_and_audio(staging_with_mixed_items: Path) -> None:
    extensions = (".mp3", ".flac", ".wav", ".aiff")
    items = organize.scan_staging(staging_with_mixed_items, extensions)
    sources = sorted(item.source.name for item in items)
    assert sources == ["Artist - Album.zip", "loose-track.mp3"]


def test_scan_skips_hidden_files(staging_with_mixed_items: Path) -> None:
    items = organize.scan_staging(staging_with_mixed_items, (".mp3",))
    assert all(not item.source.name.startswith(".") for item in items)


def test_scan_warns_and_skips_top_level_folders(tmp_path: Path, caplog) -> None:
    staging = tmp_path / "staging"
    staging.mkdir()
    (staging / "subfolder").mkdir()

    with caplog.at_level("WARNING"):
        items = organize.scan_staging(staging, (".mp3",))

    assert items == []
    assert any("subfolder" in record.message for record in caplog.records)
