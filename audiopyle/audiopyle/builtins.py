import logging
import os
import re
from typing import Optional, Union

import win32con
import win32file


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
        raise FileNotFoundError(f"File or Directory not found: {filepath}")

    return exists


def ensure_directory(filepath: str, raise_on_not_exists: bool = True) -> bool:
    """Ensure that a filepath is a directory. If it is not, raise an exception or return False.

    Args:
        filepath (str): Path to Directory
        raise_on_not_exists (bool): Raise an exception if the given filepath is not a directory.

    Raises:
        NotADirectoryError: If raise_on_not_exists is True and the directory does not exist.

    Returns:
        bool: filepath is a directory.
    """
    isdir = os.path.isdir(filepath)

    if not isdir and raise_on_not_exists:
        raise NotADirectoryError(f"Given filepath is not a directory: {filepath}")

    return isdir


def is_audio(filepath: str) -> bool:
    """Checks if a file is an audio file."""
    audio_regex = r"\.(mp3)$"
    return re.search(audio_regex, filepath, re.IGNORECASE) is not None


def count_files(directory: str) -> int:
    """Counts the number of files in a directory and its subdirectories."""
    count = sum([len(files) for _, _, files in os.walk(directory)])
    return count


def get_creation_time(path):
    return win32file.GetFileTime(
        win32file.CreateFile(
            path,
            win32con.GENERIC_READ,
            0,
            None,
            win32con.OPEN_EXISTING,
            win32con.FILE_ATTRIBUTE_NORMAL,
            None,
        )
    )[0]


def set_creation_time(path, creation_time):
    fh = win32file.CreateFile(
        path,
        win32con.GENERIC_WRITE,
        0,
        None,
        win32con.OPEN_EXISTING,
        win32con.FILE_ATTRIBUTE_NORMAL,
        None,
    )
    win32file.SetFileTime(fh, creation_time, None, None)
    fh.close()


def sanitize_directory_name(name: str):
    # Define the regex pattern for invalid characters
    invalid_chars_pattern = r'[<>:"/\\|?*]'

    # Replace invalid characters with an underscore
    sanitized_name = re.sub(invalid_chars_pattern, "-", name)

    return sanitized_name
