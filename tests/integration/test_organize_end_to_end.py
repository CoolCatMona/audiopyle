"""End-to-end tests for the audiopyle CLI."""

from __future__ import annotations

import os
import zipfile
from datetime import datetime
from pathlib import Path

import pytest
from typer.testing import CliRunner

from audiopyle.cli import app

pytestmark = pytest.mark.integration


def _make_zip(path: Path, members: dict[str, bytes]) -> None:
    with zipfile.ZipFile(path, "w") as zf:
        for name, content in members.items():
            zf.writestr(name, content)


def test_organize_dry_run_lists_actions(tmp_path: Path) -> None:
    runner = CliRunner()
    staging = tmp_path / "staging"
    staging.mkdir()
    archive = staging / "Artist - Album.zip"
    _make_zip(archive, {"01.mp3": b"a", "02.mp3": b"b"})

    library = tmp_path / "library"
    library.mkdir()

    result = runner.invoke(
        app,
        [
            "organize",
            "--staging",
            str(staging),
            "--library",
            str(library),
            "--dry-run",
            "--config",
            str(tmp_path / "missing.toml"),
        ],
    )

    assert result.exit_code == 0, result.output
    assert "Artist - Album" in result.output
    assert archive.exists()
    assert list(library.iterdir()) == []


def test_organize_writes_tree(tmp_path: Path) -> None:
    runner = CliRunner()
    staging = tmp_path / "staging"
    staging.mkdir()
    archive = staging / "Artist - Album.zip"
    _make_zip(archive, {"01.mp3": b"a", "02.mp3": b"b"})

    when = datetime(2026, 5, 21).timestamp()
    os.utime(archive, (when, when))

    library = tmp_path / "library"
    library.mkdir()

    result = runner.invoke(
        app,
        [
            "organize",
            "--staging",
            str(staging),
            "--library",
            str(library),
            "--config",
            str(tmp_path / "missing.toml"),
        ],
    )

    assert result.exit_code == 0, result.output
    assert (library / "2026" / "05 - May" / "Artist - Album" / "01.mp3").exists()


def test_config_init_writes_file(tmp_path: Path) -> None:
    runner = CliRunner()
    target = tmp_path / "config.toml"

    result = runner.invoke(app, ["config", "init", "--path", str(target)])

    assert result.exit_code == 0, result.output
    assert target.exists()
    assert "[paths]" in target.read_text()


def test_config_show_prints_resolved(tmp_path: Path) -> None:
    runner = CliRunner()
    cfg = tmp_path / "config.toml"
    cfg.write_text(f'[paths]\nstaging = "{tmp_path / "stage"}"\nlibrary = "{tmp_path / "lib"}"\n')

    result = runner.invoke(app, ["config", "show", "--config", str(cfg)])

    assert result.exit_code == 0, result.output
    assert str(tmp_path / "stage") in result.output
