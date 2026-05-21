# Default recipe -- list available recipes
default:
    @just --list

# One-time setup: ensure uv is installed, sync deps, install pre-commit hooks.
install:
    @command -v uv >/dev/null 2>&1 || curl -LsSf https://astral.sh/uv/install.sh | sh
    uv sync
    uv run pre-commit install

# Sync the virtualenv with pyproject.toml + uv.lock.
sync:
    uv sync

# Run the full test suite. Extra args are forwarded.
test *ARGS:
    uv run pytest tests {{ARGS}}

# Run only unit tests.
unit *ARGS:
    uv run pytest tests/unit {{ARGS}}

# Run only integration tests.
integration *ARGS:
    uv run pytest tests/integration {{ARGS}}

# Lint source + tests with ruff.
lint:
    uv run ruff check src tests

# Format source + tests with ruff.
format:
    uv run ruff format src tests

# Type-check source with mypy.
typecheck:
    uv run mypy src

# Run all pre-commit hooks against all files.
precommit:
    uv run pre-commit run --all-files

# Invoke the audiopyle CLI. Extra args are forwarded.
run *ARGS:
    uv run audiopyle {{ARGS}}

# Remove caches and build artifacts.
clean:
    rm -rf .pytest_cache .ruff_cache .mypy_cache dist build
