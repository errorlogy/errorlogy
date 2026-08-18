# Rebuild Errorlogy desktop app and update Start Menu shortcut.
# Run from repo: powershell -ExecutionPolicy Bypass -File errorlogy-gui\scripts\reinstall-shortcut.ps1

$GuiRoot = Split-Path $PSScriptRoot -Parent
Set-Location $GuiRoot

Write-Host "Building Errorlogy GUI..." -ForegroundColor Cyan
npm run electron:build
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$exe = Join-Path $GuiRoot "dist-electron\win-unpacked\Errorlogy.exe"
$work = Join-Path $GuiRoot "dist-electron\win-unpacked"
$shortcut = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Errorlogy.lnk"

$sh = New-Object -ComObject WScript.Shell
$lnk = $sh.CreateShortcut($shortcut)
$lnk.TargetPath = $exe
$lnk.WorkingDirectory = $work
$lnk.Description = "Errorlogy MAS — governance error analytics"
$lnk.Save()

Write-Host "Shortcut updated -> $exe" -ForegroundColor Green
Write-Host "Close any running Errorlogy window, then launch from Start Menu again." -ForegroundColor Yellow
