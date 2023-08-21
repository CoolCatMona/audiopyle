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
