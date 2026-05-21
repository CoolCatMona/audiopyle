# scripts/setup-windows.ps1
# Bootstrap a working audiopyle development environment on Windows.

$ErrorActionPreference = "Stop"

function Ensure-Tool {
    param(
        [string]$Name,
        [string]$WingetId,
        [string]$ChocoId
    )

    if (Get-Command $Name -ErrorAction SilentlyContinue) {
        Write-Host "$Name already installed."
        return
    }

    if (Get-Command winget -ErrorAction SilentlyContinue) {
        Write-Host "Installing $Name via winget..."
        winget install --id $WingetId --silent --accept-package-agreements --accept-source-agreements
    } elseif (Get-Command choco -ErrorAction SilentlyContinue) {
        Write-Host "Installing $Name via choco..."
        choco install $ChocoId -y
    } else {
        Write-Error "Neither winget nor choco is available. Install one and re-run."
    }
}

Ensure-Tool -Name uv -WingetId "astral-sh.uv" -ChocoId "uv"
Ensure-Tool -Name just -WingetId "Casey.Just" -ChocoId "just"
Ensure-Tool -Name ffmpeg -WingetId "Gyan.FFmpeg" -ChocoId "ffmpeg"

if (-not (Get-Command pre-commit -ErrorAction SilentlyContinue)) {
    Write-Host "Installing pre-commit via uv tool..."
    uv tool install pre-commit
}

Write-Host "Syncing Python dependencies with uv..."
uv sync

Write-Host "Installing pre-commit hooks..."
uv run pre-commit install

Write-Host ""
Write-Host "Setup complete. Try: just run organize --help"
