# Setting up audiopyle

audiopyle ships per-platform bootstrap scripts that install everything you
need: `uv` (package manager), `just` (task runner), `ffmpeg` (used by the
audio metadata reader), and `pre-commit`.

## macOS

Requires [Homebrew](https://brew.sh/).

```sh
./scripts/setup-macos.sh
```

Installs `uv`, `just`, `ffmpeg`, and `pre-commit` via Homebrew, syncs the
project virtualenv, and installs pre-commit hooks.

## Ubuntu / Debian

```sh
./scripts/setup-ubuntu.sh
```

Installs `ffmpeg` via `apt` (using `sudo`) and the rest via `pipx` (or
falls back to `uv`'s installer script and `just`'s installer when `pipx`
is not present), then syncs the project virtualenv and installs the
pre-commit hooks.

## Windows

Run from PowerShell (Windows Terminal recommended). Uses `winget` by
default and falls back to `choco` if available.

```powershell
.\scripts\setup-windows.ps1
```

Installs `uv`, `just`, `ffmpeg`, and `pre-commit`, syncs the project
virtualenv, and installs pre-commit hooks.

## Manual setup

If you prefer to install the tools yourself:

1. Install `uv` -- https://docs.astral.sh/uv/
2. Install `just` -- https://just.systems/
3. Install `ffmpeg` for your platform.
4. Run `uv sync` in the repo root.
5. Run `uv run pre-commit install` to enable pre-commit.

Once installed, try `just` (lists the available recipes) or
`just run organize --help`.
