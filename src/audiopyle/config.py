"""Configuration loading and merging.

A :class:`Config` instance holds the resolved values after applying:

1. Built-in defaults.
2. Values from a TOML config file (when present).
3. CLI overrides (highest precedence).

Use :func:`load_config` to start from the file (or defaults), then call
:func:`merge_overrides` with the CLI values.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

from platformdirs import user_config_dir

from audiopyle.builtins import DEFAULT_AUDIO_EXTENSIONS
from audiopyle.exceptions import ConfigError

APP_NAME = "audiopyle"
CONFIG_FILE_NAME = "config.toml"


@dataclass(frozen=True)
class Config:
    """The fully-resolved configuration for one ``audiopyle`` run.

    Attributes:
        staging: Source directory to scan. ``None`` means "not configured".
        library: Destination root for the organized tree. ``None`` means
            "not configured".
        audio_extensions: File suffixes that count as audio (lower-case,
            with leading dot).
        dry_run: When ``True``, the pipeline prints actions but writes
            nothing.
    """

    staging: Path | None
    library: Path | None
    audio_extensions: tuple[str, ...]
    dry_run: bool


def default_config_path() -> Path:
    """Return the per-user config file location for this platform."""
    return Path(user_config_dir(APP_NAME)) / CONFIG_FILE_NAME


def load_config(path: Path | None = None) -> Config:
    """Load configuration from ``path`` (or the platform default).

    Args:
        path: An explicit path to a config TOML file. When ``None``,
            :func:`default_config_path` is used.

    Returns:
        A populated :class:`Config`. If the file does not exist, defaults
        are returned with ``staging`` and ``library`` set to ``None``.

    Raises:
        ConfigError: When the file exists but cannot be parsed.
    """
    target = path or default_config_path()
    if not target.exists():
        return Config(
            staging=None,
            library=None,
            audio_extensions=DEFAULT_AUDIO_EXTENSIONS,
            dry_run=False,
        )

    try:
        data: dict[str, Any] = tomllib.loads(target.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError(f"Could not parse {target}: {exc}") from exc

    paths: dict[str, Any] = data.get("paths", {})
    organize: dict[str, Any] = data.get("organize", {})

    staging = _resolve_path(paths.get("staging"))
    library = _resolve_path(paths.get("library"))

    extensions_raw = organize.get("audio_extensions") or list(DEFAULT_AUDIO_EXTENSIONS)
    extensions = tuple(str(ext).lower() for ext in extensions_raw)

    return Config(
        staging=staging,
        library=library,
        audio_extensions=extensions,
        dry_run=bool(organize.get("dry_run", False)),
    )


def merge_overrides(config: Config, **overrides: Any) -> Config:
    """Return ``config`` with any non-``None`` overrides applied.

    Args:
        config: The base configuration.
        **overrides: Field values that should replace the corresponding
            attribute in ``config`` when they are not ``None``.

    Returns:
        A new :class:`Config` with the overrides applied.
    """
    return replace(config, **{k: v for k, v in overrides.items() if v is not None})


def write_default_config(path: Path) -> None:
    """Write a starter ``config.toml`` to ``path``.

    The file is created with placeholder paths the user is expected to
    edit. The function does not overwrite an existing file.

    Args:
        path: Destination file (its parent is created if needed).

    Raises:
        FileExistsError: If ``path`` already exists.
    """
    if path.exists():
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "[paths]\n"
        'staging = "~/Desktop/staging"\n'
        'library = "~/Music"\n'
        "\n"
        "[organize]\n"
        'audio_extensions = [".mp3", ".flac", ".wav", ".aiff"]\n'
        "dry_run = false\n",
        encoding="utf-8",
    )


def _resolve_path(value: Any) -> Path | None:
    if not value:
        return None
    return Path(str(value)).expanduser().resolve()
