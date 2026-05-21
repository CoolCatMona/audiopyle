"""Tests for ``audiopyle.config``."""

from pathlib import Path

import pytest

from audiopyle import config
from audiopyle.exceptions import ConfigError


def test_load_returns_defaults_when_no_file(tmp_path: Path) -> None:
    """``load_config`` produces sensible defaults when the file is missing."""
    cfg = config.load_config(tmp_path / "missing.toml")
    assert isinstance(cfg, config.Config)
    assert cfg.audio_extensions == (".mp3", ".flac", ".wav", ".aiff")
    assert cfg.dry_run is False


def test_load_reads_paths_and_extensions(tmp_path: Path) -> None:
    """``load_config`` reads the documented schema."""
    cfg_path = tmp_path / "config.toml"
    cfg_path.write_text(
        '[paths]\n'
        'staging = "~/Desktop/staging"\n'
        'library = "~/Music"\n'
        '\n'
        '[organize]\n'
        'audio_extensions = [".mp3", ".flac"]\n'
        'dry_run = true\n'
    )

    cfg = config.load_config(cfg_path)
    assert cfg.audio_extensions == (".mp3", ".flac")
    assert cfg.dry_run is True
    assert cfg.staging is not None and cfg.staging.is_absolute()
    assert cfg.library is not None and cfg.library.is_absolute()


def test_load_raises_on_bad_toml(tmp_path: Path) -> None:
    cfg_path = tmp_path / "bad.toml"
    cfg_path.write_text("not = valid = toml")
    with pytest.raises(ConfigError):
        config.load_config(cfg_path)


def test_merge_overrides_prefers_cli_values(tmp_path: Path) -> None:
    """CLI overrides take precedence over file values."""
    cfg = config.Config(
        staging=tmp_path / "stage",
        library=tmp_path / "lib",
        audio_extensions=(".mp3",),
        dry_run=False,
    )

    merged = config.merge_overrides(
        cfg,
        staging=tmp_path / "other-stage",
        dry_run=True,
    )

    assert merged.staging == tmp_path / "other-stage"
    assert merged.library == tmp_path / "lib"
    assert merged.dry_run is True


def test_default_config_path_uses_platformdirs() -> None:
    """``default_config_path`` returns a per-user path under a ``audiopyle`` dir."""
    path = config.default_config_path()
    assert path.name == "config.toml"
    assert "audiopyle" in str(path)
