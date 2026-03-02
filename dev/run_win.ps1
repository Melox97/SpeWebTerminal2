param(
  [string]$Port = "COM15",
  [int]$Baud = 115200,
  [string]$Host = "127.0.0.1",
  [int]$HttpPort = 8080
)

$ErrorActionPreference = "Stop"

# Go to repo root (folder containing this script's parent)
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $RepoRoot

Write-Host "Repo root: $RepoRoot"
Write-Host "Using Port=$Port Baud=$Baud Host=$Host HttpPort=$HttpPort"

# Activate venv
$Activate = Join-Path $RepoRoot ".venv\Scripts\Activate.ps1"
if (!(Test-Path $Activate)) {
  Write-Host "Virtualenv not found at .venv. Create it with: python -m venv .venv" -ForegroundColor Yellow
  exit 2
}

. $Activate

# Ensure deps
python -m pip install -U pip | Out-Null
pip install -r requirements.txt

# Set env vars for this process
$env:SPE_SERIAL_PORT = $Port
$env:SPE_SERIAL_BAUD = "$Baud"
$env:SPE_BIND_HOST = $Host
$env:SPE_HTTP_PORT = "$HttpPort"

python apps/speweb.py
