#!/usr/bin/env bash
# scripts/setup-macos.sh
# Bootstrap a working audiopyle development environment on macOS.

set -euo pipefail

if ! command -v brew >/dev/null 2>&1; then
    echo "Homebrew is required. Install from https://brew.sh and re-run." >&2
    exit 1
fi

echo "Installing system dependencies via Homebrew..."
brew install uv just ffmpeg pre-commit

echo "Syncing Python dependencies with uv..."
uv sync

echo "Installing pre-commit hooks..."
uv run pre-commit install

echo
echo "Setup complete. Try: just run organize --help"
