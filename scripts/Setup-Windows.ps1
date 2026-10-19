$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
Write-Host "`n=== FlyRank Image Relevance: Windows setup ===" -ForegroundColor Cyan
if (-not (Get-Command python -ErrorAction SilentlyContinue)) { throw "Python not found. Install Python 3.11+ and enable Add Python to PATH." }
Write-Host ("Python: " + (python -c "import sys; print(sys.version.split()[0])"))
if (-not (Test-Path ".venv\Scripts\python.exe")) { python -m venv .venv }
$Py = Join-Path $Root ".venv\Scripts\python.exe"
& $Py -m pip install --upgrade pip
& $Py -m pip install -r requirements.txt
if (-not (Test-Path ".env")) { Copy-Item ".env.example" ".env"; Write-Host "Created .env; local demo mode needs no API key." -ForegroundColor Yellow }
& $Py -m app.seed
Write-Host "`n=== Running tests ===" -ForegroundColor Cyan
& $Py -m pytest -q
if ($LASTEXITCODE -ne 0) { throw "Tests failed. Fix them before starting the server." }
Write-Host "`nDocs: http://127.0.0.1:8000/docs" -ForegroundColor Green
& $Py -m uvicorn app.main:app --host 127.0.0.1 --port 8000
