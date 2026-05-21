"""Sanity checks for the project exception hierarchy."""

import pytest

from audiopyle.exceptions import (
    AudiopyleError,
    ConfigError,
    ConflictError,
    ExtractionError,
)


@pytest.mark.parametrize("cls", [ExtractionError, ConfigError, ConflictError])
def test_subclasses_inherit_from_audiopyle_error(cls):
    assert issubclass(cls, AudiopyleError)
    assert issubclass(cls, Exception)
