"""Test classes and methods defined in the audiopyle.core module"""
import pytest
from audiopyle import core
from typing import Self
from pathlib import Path


class DummyFile(core.File):
    """Dummy Subclass of File to ensure abstract methods are implemented"""

    @classmethod
    def _from_filepath(cls, filepath: str = "/path/to/foo.txt") -> Self:
        return cls(_filename=Path(filepath).name, _filepath=filepath)


@pytest.fixture(scope="function")
def fx_temp_dir(tmp_path):
    """Creates a temporary directory for testing."""
    d = tmp_path / "test_dir"
    d.mkdir()
    p = d / "test_file.txt"
    p.write_text("test")
    yield d


@pytest.fixture(scope="function")
def fx_other_dir(tmp_path):
    """Creates a temporary directory for testing."""
    d = tmp_path / "test_dir2"
    d.mkdir()
    yield d


@pytest.fixture(scope="function")
def file():
    return DummyFile("foo.txt", "/path/to/foo.txt")


def test_file_dict(file):
    assert file.__dict__ == {"_filename": "foo.txt", "_filepath": "/path/to/foo.txt"}


def test_file_json(file):
    assert file.json == '{"_filename": "foo.txt", "_filepath": "/path/to/foo.txt"}'


def test_from_filepath(file):
    assert DummyFile._from_filepath("/path/to/foo.txt") == file


def test_move(fx_temp_dir, fx_other_dir):
    # TODO: Need to cleanup mock filesystem?
    filepath = fx_temp_dir / "test_file.txt"
    f = DummyFile._from_filepath(filepath.resolve())
    f.move(target_directory=fx_other_dir)
    expected_result = fx_other_dir / "test_file.txt"
    assert f._filepath == expected_result
    # assert False
