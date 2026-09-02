$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
Write-Host "Starting HELIOGUARD ARABIA v1.0.1..." -ForegroundColor Cyan

if (-not (Test-Path ".\HELIOGUARD_SERVER.py")) {
    Write-Host "HELIOGUARD_SERVER.py was not found. Keep all files in the same folder." -ForegroundColor Red
    Read-Host "Press Enter to close"
    exit 1
}

$py = Get-Command py -ErrorAction SilentlyContinue
if ($py) {
    & py -3 ".\HELIOGUARD_SERVER.py"
    exit $LASTEXITCODE
}

$python = Get-Command python -ErrorAction SilentlyContinue
if ($python) {
    & python ".\HELIOGUARD_SERVER.py"
    exit $LASTEXITCODE
}

Write-Host "Python was not found. Install Python and try again." -ForegroundColor Red
Read-Host "Press Enter to close"
exit 1
