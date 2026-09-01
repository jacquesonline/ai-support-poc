$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonPath = Join-Path $projectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $pythonPath)) {
    throw "No local virtual environment was found. Follow the README quick-start steps first."
}

Set-Location $projectRoot
$env:AI_PROVIDER = "fake"
$env:TICKET_BACKEND = "memory"
& $pythonPath -m uvicorn app.main:app --host 127.0.0.1 --port 8000
