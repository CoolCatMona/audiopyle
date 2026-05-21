"""Small shared helpers: logging setup and lightweight filesystem checks."""

from __future__ import annotations

import logging
import os
import re
import sys
from collections.abc import Iterable
from typing import ClassVar

DEFAULT_AUDIO_EXTENSIONS: tuple[str, ...] = (".mp3", ".flac", ".wav", ".aiff")


class CustomFormatter(logging.Formatter):
    """A colorized log formatter that respects whether stdout is a TTY."""

    cyan = "\x1b[36;1m"
    green = "\x1b[32;1m"
    yellow = "\x1b[33;1m"
    red = "\x1b[31;1m"
    magenta = "\x1b[35;1m"
    reset = "\x1b[0m"

    level_fmt = "[%(levelname)s]"
    body_fmt = "[%(asctime)s] %(message)s (%(filename)s:%(lineno)d)"

    color_map: ClassVar[dict[int, str]] = {
        logging.DEBUG: cyan,
        logging.INFO: green,
        logging.WARNING: yellow,
        logging.ERROR: red,
        logging.CRITICAL: magenta,
    }

    def __init__(self, *, use_color: bool | None = None) -> None:
        """Initialize the formatter.

        Args:
            use_color: If ``True``, always emit ANSI color codes. If
                ``False``, never. If ``None`` (default), color is enabled
                only when ``sys.stdout`` is a TTY.
        """
        super().__init__()
        self._use_color = sys.stdout.isatty() if use_color is None else use_color

    def format(self, record: logging.LogRecord) -> str:
        """Format ``record`` with optional ANSI color and full body."""
        if self._use_color:
            color = self.color_map.get(record.levelno, "")
            fmt = f"{color}{self.level_fmt}{self.reset}{self.body_fmt}"
        else:
            fmt = f"{self.level_fmt}{self.body_fmt}"
        return logging.Formatter(fmt).format(record)


def get_or_configure_logger(
    name: str,
    logger: logging.Logger | None = None,
    log_level: int | str = "WARNING",
) -> logging.Logger:
    """Return a logger configured with the project's custom formatter.

    Args:
        name: Logger name (typically ``__name__``).
        logger: An existing ``logging.Logger`` to configure in place.
        log_level: Either a string ("DEBUG", "INFO", ...) or an int level.

    Returns:
        The configured logger. Handlers are reset so repeated calls do not
        attach duplicate handlers.
    """
    logger = logger or logging.getLogger(name)
    logger.handlers.clear()

    if isinstance(log_level, str):
        log_level = logging.getLevelName(log_level.upper())

    logger.setLevel(log_level)

    handler = logging.StreamHandler()
    handler.setLevel(log_level)
    handler.setFormatter(CustomFormatter())
    logger.addHandler(handler)

    return logger


def ensure_exists(filepath: str | os.PathLike[str], raise_on_not_exists: bool = True) -> bool:
    """Return whether ``filepath`` exists; optionally raise if it does not.

    Args:
        filepath: The path to check.
        raise_on_not_exists: If True (default), raise ``FileNotFoundError``
            when the path does not exist.

    Returns:
        ``True`` if the path exists, ``False`` otherwise.

    Raises:
        FileNotFoundError: If ``raise_on_not_exists`` is ``True`` and the
            path does not exist.
    """
    exists = os.path.exists(filepath)
    if not exists and raise_on_not_exists:
        raise FileNotFoundError(f"File or Directory not found: {filepath}")
    return exists


def ensure_directory(filepath: str | os.PathLike[str], raise_on_not_exists: bool = True) -> bool:
    """Return whether ``filepath`` is a directory; optionally raise if not.

    Args:
        filepath: The path to check.
        raise_on_not_exists: If True (default), raise ``NotADirectoryError``
            when the path is not a directory.

    Returns:
        ``True`` if the path is a directory, ``False`` otherwise.

    Raises:
        NotADirectoryError: If ``raise_on_not_exists`` is ``True`` and the
            path is not a directory.
    """
    isdir = os.path.isdir(filepath)
    if not isdir and raise_on_not_exists:
        raise NotADirectoryError(f"Given filepath is not a directory: {filepath}")
    return isdir


def is_audio(
    filepath: str | os.PathLike[str],
    extensions: Iterable[str] = DEFAULT_AUDIO_EXTENSIONS,
) -> bool:
    """Return whether ``filepath`` is a recognized audio file by extension.

    Args:
        filepath: The path to check.
        extensions: An iterable of lower-case suffixes including the dot.
            Defaults to :data:`DEFAULT_AUDIO_EXTENSIONS`.

    Returns:
        ``True`` if the suffix is one of the recognized audio extensions.
    """
    suffix = os.path.splitext(str(filepath))[1].lower()
    return suffix in {ext.lower() for ext in extensions}


def count_files(directory: str | os.PathLike[str]) -> int:
    """Return the recursive count of regular files under ``directory``.

    Args:
        directory: The root directory to walk.

    Returns:
        The number of regular files at or below ``directory``.
    """
    return sum(len(files) for _, _, files in os.walk(directory))


def sanitize_directory_name(name: str) -> str:
    """Replace characters that are illegal in directory names with ``-``.

    Args:
        name: The candidate name.

    Returns:
        A safe directory name with invalid characters replaced.
    """
    return re.sub(r'[<>:"/\\|?*]', "-", name)
