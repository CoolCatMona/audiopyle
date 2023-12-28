"""Test builtin methods for audiopyle"""
import pytest
import logging
import os
from audiopyle import builtins


def test_get_or_configure_logger():
    logger = builtins.get_or_configure_logger("test_logger", logLevel="DEBUG")
    assert logger.name == "test_logger"
    assert logger.level == logging.DEBUG
    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0], logging.StreamHandler)


@pytest.mark.parametrize(
    "filepath, raise_on_not_exists, expected_result",
    [
        (os.path.join(os.path.dirname(__file__), "test_data", "foo.txt"), True, True),
        ("bar.txt", True, FileNotFoundError),
        ("bar.txt", False, False),
    ],
    ids=["file_exists", "raises_FileNotFound", "file_does_not_exist"],
)
def test_ensure_exists(filepath, raise_on_not_exists, expected_result):
    if type(expected_result) == type and issubclass(expected_result, Exception):
        with pytest.raises(expected_result):
            builtins.ensure_exists(filepath, raise_on_not_exists)
    else:
        assert builtins.ensure_exists(filepath, raise_on_not_exists) == expected_result


@pytest.mark.parametrize(
    "dirpath, raise_on_not_exists, expected_result",
    [
        (os.path.join(os.path.dirname(__file__), "test_data"), True, True),
        ("bar", True, NotADirectoryError),
        ("bar", False, False),
    ],
    ids=["directory_exists", "raises_NotADirectory", "directory_does_not_exist"],
)
def test_ensure_directory(dirpath, raise_on_not_exists, expected_result):
    if type(expected_result) == type and issubclass(expected_result, Exception):
        with pytest.raises(expected_result):
            builtins.ensure_directory(dirpath, raise_on_not_exists)
    else:
        assert (
            builtins.ensure_directory(dirpath, raise_on_not_exists) == expected_result
        )


@pytest.mark.parametrize(
    "filename,expected_result",
    [
        ("file.mp3", True),
        ("test/files/file.mp3", True),
        ("file.bar", False),
        ("test/mp3/file.bar", False),
    ],
    ids=[
        "mp3",
        "absolute_path",
        "not_audio",
        "not_audio_absolute_path",
    ],
)
def test_is_audio(filename, expected_result):
    assert builtins.is_audio(filename) == expected_result


@pytest.mark.parametrize(
    "directory,expected_result",
    [
        (os.path.join(os.path.dirname(__file__), "test_data"), 2),
        (os.path.join(os.path.dirname(__file__), "test_data", "test_subdirectory"), 1),
    ],
    ids=[
        "counts_including_subdirectories",
        "counts_single_directory",
    ],
)
def test_count_files(directory, expected_result):
    assert builtins.count_files(directory) == expected_result
