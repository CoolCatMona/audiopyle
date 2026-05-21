"""Sanity checks for the project exception hierarchy."""

import pytest

from audiopyle.exceptions import (
    AudiopyleError,
    ConfigError,
    ExtractionError,
)


@pytest.mark.parametrize("cls", [ExtractionError, ConfigError])
def test_subclasses_inherit_from_audiopyle_error(cls):
    assert issubclass(cls, AudiopyleError)
    assert issubclass(cls, Exception)
