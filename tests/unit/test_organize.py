"""Tests for the staging-to-library organize pipeline."""

from __future__ import annotations

import zipfile
from datetime import datetime
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


def test_classify_multi_track_zip_is_album(tmp_path: Path) -> None:
    archive = tmp_path / "album.zip"
    _make_zip(archive, {"01.mp3": b"", "02.mp3": b""})
    item = organize.StagedItem(source=archive, is_archive=True, mtime=datetime.now())
    assert organize.classify(item, (".mp3",)) is organize.ItemKind.ALBUM_ARCHIVE


def test_classify_single_track_zip_is_single(tmp_path: Path) -> None:
    archive = tmp_path / "single.zip"
    _make_zip(archive, {"01.mp3": b"a"})
    item = organize.StagedItem(source=archive, is_archive=True, mtime=datetime.now())
    assert organize.classify(item, (".mp3",)) is organize.ItemKind.SINGLE_FILE


def test_classify_loose_audio_is_single(tmp_path: Path) -> None:
    file = tmp_path / "track.flac"
    file.write_bytes(b"a")
    item = organize.StagedItem(source=file, is_archive=False, mtime=datetime.now())
    assert organize.classify(item, (".mp3", ".flac")) is organize.ItemKind.SINGLE_FILE


def test_classify_empty_zip_is_ignored(tmp_path: Path) -> None:
    archive = tmp_path / "empty.zip"
    _make_zip(archive, {"readme.txt": b""})
    item = organize.StagedItem(source=archive, is_archive=True, mtime=datetime.now())
    assert organize.classify(item, (".mp3",)) is organize.ItemKind.IGNORED


def test_organize_moves_album_into_year_month_folder(tmp_path: Path) -> None:
    staging = tmp_path / "staging"
    staging.mkdir()
    archive = staging / "Artist - Album.zip"
    _make_zip(archive, {"01.mp3": b"a", "02.mp3": b"b"})
    import os

    target_time = datetime(2026, 5, 21, 12, 0, 0)
    os.utime(archive, (target_time.timestamp(), target_time.timestamp()))

    library = tmp_path / "library"
    library.mkdir()

    results = organize.organize(
        staging=staging,
        library=library,
        audio_extensions=(".mp3",),
        dry_run=False,
    )

    expected_dir = library / "2026" / "05 - May" / "Artist - Album"
    assert (expected_dir / "01.mp3").read_bytes() == b"a"
    assert (expected_dir / "02.mp3").read_bytes() == b"b"
    assert not archive.exists()
    assert any(r.ok for r in results)


def test_organize_moves_loose_single_into_year_month(tmp_path: Path) -> None:
    staging = tmp_path / "staging"
    staging.mkdir()
    track = staging / "Track.mp3"
    track.write_bytes(b"a")
    import os

    target_time = datetime(2026, 5, 21, 12, 0, 0)
    os.utime(track, (target_time.timestamp(), target_time.timestamp()))

    library = tmp_path / "library"
    library.mkdir()

    organize.organize(staging, library, (".mp3",), dry_run=False)

    assert (library / "2026" / "05 - May" / "Track.mp3").read_bytes() == b"a"
    assert not track.exists()


def test_organize_dry_run_writes_nothing(tmp_path: Path) -> None:
    staging = tmp_path / "staging"
    staging.mkdir()
    track = staging / "Track.mp3"
    track.write_bytes(b"a")

    library = tmp_path / "library"
    library.mkdir()

    organize.organize(staging, library, (".mp3",), dry_run=True)

    assert track.exists()
    assert list(library.iterdir()) == []


def test_organize_merges_into_existing_album_folder(tmp_path: Path) -> None:
    library = tmp_path / "library"
    existing = library / "2026" / "05 - May" / "Artist - Album"
    existing.mkdir(parents=True)
    (existing / "01.mp3").write_bytes(b"existing")

    staging = tmp_path / "staging"
    staging.mkdir()
    archive = staging / "Artist - Album.zip"
    _make_zip(archive, {"01.mp3": b"new", "02.mp3": b"b"})
    import os

    when = datetime(2026, 5, 21).timestamp()
    os.utime(archive, (when, when))

    organize.organize(staging, library, (".mp3",), dry_run=False)

    assert (existing / "01.mp3").read_bytes() == b"existing"
    assert (existing / "02.mp3").read_bytes() == b"b"
