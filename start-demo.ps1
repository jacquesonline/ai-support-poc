$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonPath = Join-Path $projectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $pythonPath)) {
    throw "No local virtual environment was found. Follow the README quick-start steps first."
}

Set-Location $projectRoot
$env:AI_PROVIDER = "fake"
$env:TICKET_BACKEND = "memory"
Write-Host "Starting the synthetic ABL legal-technology demonstration"
Write-Host "Overview:   http://127.0.0.1:8017/"
Write-Host "Proofs:     http://127.0.0.1:8017/workbench"
Write-Host "Rationale:  http://127.0.0.1:8017/cheatsheet"
Write-Host "Press Ctrl+C to stop."
& $pythonPath -m uvicorn app.main:app --host 127.0.0.1 --port 8017
