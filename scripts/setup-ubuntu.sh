#!/usr/bin/env bash
# scripts/setup-ubuntu.sh
# Bootstrap a working audiopyle development environment on Ubuntu/Debian.

set -euo pipefail

echo "Installing system dependencies via apt..."
sudo apt-get update
sudo apt-get install -y ffmpeg curl

install_uv() {
    if command -v uv >/dev/null 2>&1; then
        return
    fi
    if command -v pipx >/dev/null 2>&1; then
        pipx install uv
    else
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.local/bin:$PATH"
    fi
}

install_just() {
    if command -v just >/dev/null 2>&1; then
        return
    fi
    if command -v pipx >/dev/null 2>&1; then
        pipx install rust-just
    else
        curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash -s -- --to "$HOME/.local/bin"
        export PATH="$HOME/.local/bin:$PATH"
    fi
}

install_precommit() {
    if command -v pre-commit >/dev/null 2>&1; then
        return
    fi
    if command -v pipx >/dev/null 2>&1; then
        pipx install pre-commit
    else
        uv tool install pre-commit
    fi
}

install_uv
install_just
install_precommit

echo "Syncing Python dependencies with uv..."
uv sync

echo "Installing pre-commit hooks..."
uv run pre-commit install

echo
echo "Setup complete. Try: just run organize --help"
