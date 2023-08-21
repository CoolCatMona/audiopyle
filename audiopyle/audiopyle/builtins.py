import logging
import os
from typing import Optional, Union
import re


class CustomFormatter(logging.Formatter):
    cyan = "\x1b[36;1m"
    green = "\x1b[32;1m"
    yellow = "\x1b[33;1m"
    red = "\x1b[31;1m"
    magenta = "\x1b[35;1m"
    reset = "\x1b[0m"
    level = "[%(levelname)s]"
    format = "[%(asctime)s] %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: cyan + level + reset + format,
        logging.INFO: green + level + reset + format,
        logging.WARNING: yellow + level + reset + format,
        logging.ERROR: red + level + reset + format,
        logging.CRITICAL: magenta + level + reset + format,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def get_or_configure_logger(
    name: str,
    logger: Optional[logging.Logger] = None,
    logLevel: Optional[Union[int, str]] = "WARNING",
) -> logging.Logger:
    """Initializes a logger object with a custom formatter and a console stream handler at a specific level
    Arguments:
        name (str): Reference name to the logger
        logger (logging.Logger, Optional): Logger object to be initialized
        logLevel (str, int, Optional): The logging level to set for the logger. Defaults to 'WARNING'.
    Example:
        logger = get_or_configure_logger(__name__)
    """
    logger = logger or logging.getLogger(name)

    # Clears handlers to force re-initialization
    logger.handlers.clear()

    # Convert log level to an int if it's a string
    if isinstance(logLevel, str):
        logLevel = logging.getLevelName(logLevel.upper())

    logger.setLevel(logLevel)

    # Only add new handler if the logger has no handlers
    if not logger.handlers:
        # Create console handler with a higher log level
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logLevel)
        console_handler.setFormatter(CustomFormatter())
        logger.addHandler(console_handler)

    return logger


def ensure_exists(filepath: str, raise_on_not_exists: bool = True) -> bool:
    """Ensure that a filepath exists. If it does not, raise an exception or return False.

    Args:
        filepath (str): Path to File
        raise_on_not_exists (bool): Raise an exception if the file does not exist.

    Raises:
        FileNotFoundError: If raise_on_not_exists is True and the file does not exist.

    Returns:
        bool: File exists.
    """
    exists = os.path.exists(filepath)

    if not exists and raise_on_not_exists:
        raise FileNotFoundError(f"File not found: {filepath}")

    return exists


def is_audio(filepath: str) -> bool:
    """Checks if a file is an audio file."""
    audio_regex = r"\.(mp3)$"
    return re.search(audio_regex, filepath, re.IGNORECASE) is not None


def count_files(directory: str) -> int:
    """Counts the number of files in a directory."""
    count = 0
    for root, _, files in os.walk(directory):
        for file in files:
            if is_audio(file):
                count += 1
    return count
