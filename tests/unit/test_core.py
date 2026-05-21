"""Tests for the core ``File`` dataclass."""

from pathlib import Path
from typing import Self

import pytest

from audiopyle import core


class DummyFile(core.File):
    """Concrete subclass for testing the abstract base."""

    @classmethod
    def _from_filepath(cls, filepath: str | Path = "/path/to/foo.txt") -> Self:
        return cls(filename=Path(filepath).name, filepath=str(filepath))


@pytest.fixture
def file() -> DummyFile:
    return DummyFile(filename="foo.txt", filepath="/path/to/foo.txt")


def test_to_dict(file: DummyFile) -> None:
    assert file.to_dict() == {
        "filename": "foo.txt",
        "filepath": "/path/to/foo.txt",
        "download_year": "",
        "download_month": "",
    }


def test_json(file: DummyFile) -> None:
    import json

    assert json.loads(file.json) == file.to_dict()


def test_from_filepath_round_trip(file: DummyFile) -> None:
    assert DummyFile._from_filepath("/path/to/foo.txt") == file


def test_move_preserves_filename(tmp_path: Path) -> None:
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    src = src_dir / "track.mp3"
    src.write_bytes(b"hello")

    target_dir = tmp_path / "target"

    f = DummyFile._from_filepath(src)
    f.move(target_dir)

    assert (target_dir / "track.mp3").exists()
    assert Path(f.filepath) == target_dir / "track.mp3"
