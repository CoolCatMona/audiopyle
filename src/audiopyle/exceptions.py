"""Project exception hierarchy.

All audiopyle-raised errors inherit from :class:`AudiopyleError`, so callers
can catch the whole family with a single ``except`` clause.
"""


class AudiopyleError(Exception):
    """Base class for all audiopyle errors."""


class ExtractionError(AudiopyleError):
    """Raised when a zip archive contains unsafe members or fails to extract."""


class ConfigError(AudiopyleError):
    """Raised when the configuration file is missing required fields or malformed."""


class ConflictError(AudiopyleError):
    """Raised when a destination path collision cannot be resolved by policy."""
