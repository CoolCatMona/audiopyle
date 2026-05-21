# audiopyle

audiopyle is a local music management tool. Point it at a staging
directory full of downloaded zips and loose audio files; it extracts the
zips, sorts everything into a `year / month` tree under your music
library, and leaves the staging directory empty.

```
~/Music/
  2026/
    05 - May/
      Artist - Album/
        01 - Track.mp3
      Single Track.mp3
```

## Setup

See [docs/setup.md](docs/setup.md) for per-platform instructions
(macOS, Ubuntu, Windows) and the bootstrap scripts that automate them.

## Usage

```sh
# One-time: create a starter config file.
audiopyle config init

# Preview what would happen.
audiopyle organize --dry-run

# Do it.
audiopyle organize
```

CLI flags (`--staging`, `--library`, `--config`) override values from
the config file. Run `audiopyle --help` for the full surface.

## Development

```sh
just            # list available recipes
just sync       # install/refresh deps
just test       # run all tests
just unit       # only unit tests
just lint       # ruff check
just format     # ruff format
just typecheck  # mypy
just run organize --help
```

## License

MIT.
