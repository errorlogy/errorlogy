# Errorlogy MAS — hourly ingest for Windows Task Scheduler (TZ-H1-03)
#
# Manual:  .\scripts\schedule_ingest.ps1
# Task Scheduler example:
#   schtasks /Create /TN "ErrorlogyIngest" /TR "powershell -NoProfile -ExecutionPolicy Bypass -File C:\path\to\errorlogy-mas\scripts\schedule_ingest.ps1" /SC HOURLY /RU SYSTEM
#
# Optional args forwarded to run_ingest_cron.py: --all, --dry-run, --no-analyze

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
py -3.12 scripts/run_ingest_cron.py @args
