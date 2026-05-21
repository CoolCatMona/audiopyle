"""Tests for target path computation and conflict planning."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from audiopyle import paths


def test_format_year_month_uses_full_month_name() -> None:
    year, month = paths.format_year_month(datetime(2026, 5, 21))
    assert year == "2026"
    assert month == "05 - May"


def test_compute_album_target_nests_year_month_stem(tmp_path: Path) -> None:
    target = paths.compute_album_target(
        library=tmp_path,
        when=datetime(2026, 5, 21),
        zip_stem="Some Artist - Some Album",
    )
    assert target == tmp_path / "2026" / "05 - May" / "Some Artist - Some Album"


def test_compute_single_target_is_flat(tmp_path: Path) -> None:
    target = paths.compute_single_target(
        library=tmp_path,
        when=datetime(2026, 5, 21),
        filename="Single Track.mp3",
    )
    assert target == tmp_path / "2026" / "05 - May" / "Single Track.mp3"


def test_plan_merge_skips_duplicates(tmp_path: Path) -> None:
    source = tmp_path / "src"
    source.mkdir()
    (source / "a.mp3").write_bytes(b"a")
    (source / "b.mp3").write_bytes(b"b")

    target = tmp_path / "dest"
    target.mkdir()
    (target / "a.mp3").write_bytes(b"existing")

    moves, skipped = paths.plan_merge(
        source_files=[source / "a.mp3", source / "b.mp3"],
        target_dir=target,
    )

    assert moves == [(source / "b.mp3", target / "b.mp3")]
    assert skipped == [source / "a.mp3"]
