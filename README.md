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

## Quick start

```sh
# 1. Write a starter config to the platform default location
#    (~/.config/audiopyle/config.toml on macOS/Linux,
#    %APPDATA%\audiopyle\config.toml on Windows).
audiopyle config init

# 2. Edit the file to point at your staging and library directories.

# 3. Sanity check the resolved configuration.
audiopyle config show

# 4. Preview the plan without touching disk.
audiopyle organize --dry-run

# 5. Move the files.
audiopyle organize
```

## What it does

Starting from a staging folder like this:

```
~/Desktop/staging/
  Artist - Album.zip          # contains 01.mp3, 02.mp3, cover.jpg
  Other Artist - EP.zip       # contains 01.flac, 02.flac
  Some Single.mp3
```

`audiopyle organize` produces:

```
~/Music/
  2026/
    05 - May/
      Artist - Album/
        01.mp3
        02.mp3
        cover.jpg
      Other Artist - EP/
        01.flac
        02.flac
      Some Single.mp3
```

The year and month bucket comes from the source file's mtime (or the
zip's mtime for archives). Multi-track zips become their own album
folder, named after the zip stem. Single-track zips and loose audio
files land directly in the month directory. Non-audio companions like
cover art are kept alongside the tracks they came with.

## Configuration

`config.toml`:

```toml
[paths]
staging = "~/Desktop/staging"
library = "~/Music"

[organize]
audio_extensions = [".mp3", ".flac", ".wav", ".aiff"]
dry_run = false
```

CLI flags override the file. For example, to try a different
destination without editing the config:

```sh
audiopyle organize \
  --staging ~/Downloads/new-music \
  --library /Volumes/External/Music \
  --dry-run
```

Other useful invocations:

```sh
audiopyle organize --verbose            # log every decision the pipeline makes
audiopyle organize --config ./alt.toml  # use a one-off config file
audiopyle config init --path ./alt.toml # scaffold a config somewhere specific
```

Run `audiopyle --help` (or `audiopyle organize --help`) for the full
flag surface.

## What gets skipped

- Hidden files (anything whose name starts with `.`).
- Files whose extension is not in `audio_extensions` and is not `.zip`.
- Subdirectories at the top of staging. Staging is expected to be flat;
  if you have a folder there, you will see a warning and it will be
  left alone.
- Files that would collide with something already in the library. For
  album folders this means the existing track is preserved and the new
  one is skipped. For single files at the month-directory level the
  new file is skipped entirely with a warning.

The summary line at the end of a run tells you how many albums and
singles moved, how many files were skipped for collisions, and how
many items were ignored.

## When something goes wrong

The CLI catches every audiopyle-raised error (config parsing, unsafe
zip member, extraction failure) and prints a one-line message before
exiting non-zero. You will not see a Python traceback unless something
unexpected escapes the pipeline (which is a bug worth filing).

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
