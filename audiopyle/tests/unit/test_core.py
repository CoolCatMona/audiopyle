"""Test classes and methods defined in the audiopyle.core module"""
import pytest
from audiopyle import core
from typing import Self


class DummyFile(core.File):
    """Dummy Subclass of File to ensure abstract methods are implemented"""

    @classmethod
    def _from_filepath(cls, filepath: str) -> Self:
        return cls(_filename="foo.txt", _filepath="/path/to/foo.txt")


@pytest.fixture(scope="function")
def file():
    return DummyFile("foo.txt", "/path/to/foo.txt")


def test_file_dict(file):
    assert file.__dict__ == {"_filename": "foo.txt", "_filepath": "/path/to/foo.txt"}


def test_file_json(file):
    assert file.json == '{"_filename": "foo.txt", "_filepath": "/path/to/foo.txt"}'


def test_from_filepath(file):
    assert DummyFile._from_filepath("/path/to/foo.txt") == file
