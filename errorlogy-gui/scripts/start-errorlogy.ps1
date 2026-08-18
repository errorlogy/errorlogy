# Start MAS API (if needed) and launch Errorlogy desktop app.
# Usage: powershell -ExecutionPolicy Bypass -File errorlogy-gui\scripts\start-errorlogy.ps1

$ErrorActionPreference = "Stop"
$GuiRoot = Split-Path $PSScriptRoot -Parent
$RepoRoot = Split-Path $GuiRoot -Parent
$MasDir = if ($env:ERRORLOGY_MAS_DIR) { $env:ERRORLOGY_MAS_DIR } else { Join-Path $RepoRoot "errorlogy-mas" }
$HealthUrl = "http://127.0.0.1:8000/api/health"
$LogDir = Join-Path $env:LOCALAPPDATA "errorlogy-gui"
$ApiLog = Join-Path $LogDir "api-startup.log"
$ErrorlogyExe = Join-Path $env:LOCALAPPDATA "Programs\errorlogy-gui\Errorlogy.exe"

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

function Write-ApiLog([string]$Message) {
    $line = "[$(Get-Date -Format o)] $Message"
    Add-Content -Path $ApiLog -Value $line -Encoding UTF8
}

function Test-ApiHealth {
    try {
        $r = Invoke-WebRequest -Uri $HealthUrl -UseBasicParsing -TimeoutSec 3
        return $r.StatusCode -eq 200
    } catch {
        return $false
    }
}

function Resolve-PythonExe {
    if ($env:ERRORLOGY_PYTHON -and (Test-Path $env:ERRORLOGY_PYTHON)) {
        return $env:ERRORLOGY_PYTHON
    }
    foreach ($ver in @('312', '313', '311', '310')) {
        $exe = Join-Path $env:LOCALAPPDATA "Programs\Python\Python$ver\python.exe"
        if (-not (Test-Path $exe)) { continue }
        Push-Location $MasDir
        try {
            & $exe -c "import api.main" 2>$null
            if ($LASTEXITCODE -eq 0) { return $exe }
        } finally {
            Pop-Location
        }
    }
    foreach ($pyArgs in @(@('-3.12'), @('-3'))) {
        Push-Location $MasDir
        try {
            & py @pyArgs -c "import api.main" 2>$null
            if ($LASTEXITCODE -eq 0) { return "py:$($pyArgs -join ',')" }
        } finally {
            Pop-Location
        }
    }
    return $null
}

Write-Host "=== Errorlogy launcher ===" -ForegroundColor Cyan
Write-ApiLog "`n=== start-errorlogy.ps1 $(Get-Date -Format o) ==="
Write-ApiLog "MAS_DIR=$MasDir exists=$(Test-Path $MasDir)"

if (-not (Test-Path $MasDir)) {
    Write-Host "ERROR: errorlogy-mas not found at $MasDir" -ForegroundColor Red
    Write-ApiLog "ERROR: MAS_DIR missing"
    exit 1
}

if (-not (Test-ApiHealth)) {
    $python = Resolve-PythonExe
    if (-not $python) {
        Write-Host "ERROR: No Python with MAS deps found. Install Python 3.12 and run:" -ForegroundColor Red
        Write-Host "  cd $MasDir" -ForegroundColor Yellow
        Write-Host "  py -3.12 -m pip install -r requirements.txt" -ForegroundColor Yellow
        Write-ApiLog "ERROR: no suitable Python"
        exit 1
    }

    if ($python -like "py:*") {
        $pyVer = ($python -split ':')[1]
        Write-Host "Starting MAS API (py $pyVer)..." -ForegroundColor Yellow
        Write-ApiLog "spawn: py $pyVer -m uvicorn api.main:app cwd=$MasDir"
        $proc = Start-Process -FilePath "py" `
            -ArgumentList $pyVer, "-m", "uvicorn", "api.main:app", "--host", "127.0.0.1", "--port", "8000" `
            -WorkingDirectory $MasDir -WindowStyle Hidden -PassThru
    } else {
        Write-Host "Starting MAS API ($python)..." -ForegroundColor Yellow
        Write-ApiLog "spawn: $python -m uvicorn api.main:app cwd=$MasDir"
        $proc = Start-Process -FilePath $python `
            -ArgumentList "-m", "uvicorn", "api.main:app", "--host", "127.0.0.1", "--port", "8000" `
            -WorkingDirectory $MasDir -WindowStyle Hidden -PassThru
    }

    Write-ApiLog "spawn pid=$($proc.Id)"

    $maxWait = 60
    $ready = $false
    for ($i = 1; $i -le $maxWait; $i++) {
        if (Test-ApiHealth) {
            $ready = $true
            Write-Host "API ready (${i}s)." -ForegroundColor Green
            Write-ApiLog "health OK after ${i}s"
            break
        }
        Start-Sleep -Seconds 1
    }

    if (-not $ready) {
        Write-Host "WARNING: API did not respond after ${maxWait}s. See log:" -ForegroundColor Red
        Write-Host "  $ApiLog" -ForegroundColor Yellow
        Write-ApiLog "health FAILED after ${maxWait}s"
    }
} else {
    Write-Host "API already running on :8000" -ForegroundColor Green
    Write-ApiLog "API already up"
}

if (-not (Test-Path $ErrorlogyExe)) {
    Write-Host "Errorlogy not installed. Run: powershell -ExecutionPolicy Bypass -File $GuiRoot\scripts\reinstall.ps1" -ForegroundColor Red
    exit 1
}

$env:ERRORLOGY_MAS_DIR = $MasDir
if ($python -and $python -notlike "py:*") { $env:ERRORLOGY_PYTHON = $python }

Write-Host "Launching Errorlogy..." -ForegroundColor Green
Start-Process -FilePath $ErrorlogyExe
