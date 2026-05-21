"""Command-line interface for audiopyle.

Run ``audiopyle --help`` for the full surface. Common commands:

* ``audiopyle organize`` -- drain staging into the library.
* ``audiopyle config show`` -- print the resolved configuration.
* ``audiopyle config init`` -- write a starter config file.
"""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

import typer

from audiopyle import config as config_module
from audiopyle import organize as organize_module
from audiopyle.builtins import get_or_configure_logger

app = typer.Typer(add_completion=False, help="Local music management CLI.")
config_app = typer.Typer(add_completion=False, help="Inspect or scaffold the config file.")
app.add_typer(config_app, name="config")


@app.command("organize")
def organize_cmd(
    staging: Path | None = typer.Option(None, "--staging", help="Staging directory."),
    library: Path | None = typer.Option(None, "--library", help="Library root."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Plan only; do not move files."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="DEBUG-level logging."),
    config: Path | None = typer.Option(None, "--config", help="Config file location."),
) -> None:
    """Drain ``staging`` into ``library`` organized by year and month."""
    log_level = "DEBUG" if verbose else "INFO"
    get_or_configure_logger("audiopyle", log_level=log_level)

    cfg = config_module.load_config(config)
    cfg = config_module.merge_overrides(
        cfg,
        staging=staging,
        library=library,
        dry_run=dry_run or None,
    )

    if cfg.staging is None or cfg.library is None:
        typer.echo(
            "ERROR: --staging and --library must be provided either on the CLI "
            "or in the config file."
        )
        raise typer.Exit(code=2)

    results = organize_module.organize(
        staging=cfg.staging,
        library=cfg.library,
        audio_extensions=cfg.audio_extensions,
        dry_run=cfg.dry_run,
    )

    albums = sum(
        1 for r in results if r.kind is organize_module.ItemKind.ALBUM_ARCHIVE and r.ok
    )
    singles = sum(
        1 for r in results if r.kind is organize_module.ItemKind.SINGLE_FILE and r.ok
    )
    skipped_files = sum(r.files_skipped for r in results)
    ignored = sum(
        1 for r in results if r.kind is organize_module.ItemKind.IGNORED
    )
    typer.echo(
        f"Processed: {len(results)}\n"
        f"  Albums moved:  {albums}\n"
        f"  Singles moved: {singles}\n"
        f"  Skipped:       {skipped_files} (duplicate name)\n"
        f"  Ignored:       {ignored}"
    )


@config_app.command("show")
def config_show_cmd(
    config: Path | None = typer.Option(None, "--config", help="Config file location."),
) -> None:
    """Print the resolved configuration (file values plus defaults)."""
    cfg = config_module.load_config(config)
    for key, value in asdict(cfg).items():
        typer.echo(f"{key} = {value}")


@config_app.command("init")
def config_init_cmd(
    path: Path | None = typer.Option(None, "--path", help="Where to write the file."),
) -> None:
    """Write a starter ``config.toml`` to the default per-user location."""
    target = path or config_module.default_config_path()
    if target.exists():
        typer.echo(f"Config already exists at {target}")
        raise typer.Exit(code=1)
    config_module.write_default_config(target)
    typer.echo(f"Wrote {target}")
