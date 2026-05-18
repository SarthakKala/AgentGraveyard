#Requires -Version 5.1
<#
 Agent Graveyard — one-shot setup (Windows PowerShell).
 Same intent as run.sh: venv, deps, check_env, seed, start uvicorn.

 Usage (repo root):
   .\run.ps1

 If script execution is disabled:
   Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
#>
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

function Find-Python {
    $candidates = @(
        @{ Cmd = "py"; Args = @("-3") },
        @{ Cmd = "python3"; Args = @() },
        @{ Cmd = "python"; Args = @() }
    )
    foreach ($x in $candidates) {
        if (Get-Command $x.Cmd -ErrorAction SilentlyContinue) {
            return $x
        }
    }
    Write-Host "Python not found. Install Python 3.10+ from python.org and try again."
    exit 1
}

$p = Find-Python
Write-Host ""
Write-Host "Agent Graveyard - Setup"
Write-Host "================================"

$pyExe = & $p.Cmd @($p.Args + @("--version")) 2>&1
Write-Host "Python $pyExe"

if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..."
    & $p.Cmd @($p.Args + @("-m", "venv", ".venv"))
}

$activate = Join-Path ".venv" "Scripts/Activate.ps1"
if (-not (Test-Path $activate)) {
    Write-Host "venv Scripts missing. Remove .venv and re-run."
    exit 1
}
. $activate
Write-Host "Virtual environment active"

Write-Host ""
Write-Host "Installing backend dependencies..."
python -m pip install -q -r backend/requirements.txt
Write-Host "Backend dependencies installed"

Write-Host "Installing SDK..."
python -m pip install -q -e ./sdk
Write-Host "SDK installed (graveyard CLI available)"

Write-Host "Installing demo dependencies..."
python -m pip install -q requests beautifulsoup4
Write-Host "Demo dependencies installed"

if (-not (Test-Path "backend/.env")) {
    Write-Host ""
    Write-Host "backend/.env not found."
    Write-Host "  Copy-Item backend/.env.example backend/.env"
    Write-Host "  Then fill API keys and run this script again."
    exit 1
}
Write-Host "backend/.env found"

Write-Host ""
Write-Host "Checking environment..."
python scripts/check_env.py
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Fix the issues above before continuing."
    exit 1
}

Write-Host ""
Write-Host "Seeding community failure database..."
Write-Host "(First run downloads embedding model ~400MB - please wait)"
Push-Location backend
try {
    python ../seed_data/seed.py
} finally {
    Pop-Location
}
Write-Host "Database seeded"

Write-Host ""
Write-Host "================================"
Write-Host "Setup complete!"
Write-Host ""
Write-Host "Starting backend (listening on 127.0.0.1:8000)."
Write-Host "  In your browser use: http://localhost:8000/health  (not 0.0.0.0 - that is not a valid browser URL)"
Write-Host "Press Ctrl+C to stop."
Write-Host ""
Write-Host "In a NEW PowerShell window:"
Write-Host "  .\.venv\Scripts\Activate.ps1"
Write-Host "  python demo/demo_e2e.py"
Write-Host "  python demo/demo_agent.py"
Write-Host "================================"
Write-Host ""

Set-Location backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
