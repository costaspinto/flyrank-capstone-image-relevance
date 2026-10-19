$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
Write-Host "This removes the local SQLite demo database only." -ForegroundColor Yellow
if ((Read-Host "Type RESET to continue") -ne "RESET") { Write-Host "Cancelled."; exit 0 }
if (Test-Path "image_relevance.db") { Remove-Item "image_relevance.db" -Force }
& ".\.venv\Scripts\python.exe" -m app.seed
