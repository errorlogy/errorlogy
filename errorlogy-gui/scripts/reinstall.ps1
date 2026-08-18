# Clean reinstall Errorlogy desktop app (reads version from package.json)
# Double-click or: powershell -ExecutionPolicy Bypass -File errorlogy-gui\scripts\reinstall.ps1

$ErrorActionPreference = "Stop"
$GuiRoot = Split-Path $PSScriptRoot -Parent
$PackageJson = Get-Content (Join-Path $GuiRoot "package.json") -Raw | ConvertFrom-Json
$Version = $PackageJson.version
$Installer = Join-Path $GuiRoot "dist-electron\Errorlogy Setup $Version.exe"
$OldUninst = "$env:LOCALAPPDATA\Programs\errorlogy-gui\Uninstall Errorlogy.exe"
$Installed = "$env:LOCALAPPDATA\Programs\errorlogy-gui\Errorlogy.exe"

Write-Host "=== Errorlogy reinstall (v$Version) ===" -ForegroundColor Cyan

Get-Process -Name "Errorlogy" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 1

if (Test-Path $OldUninst) {
    Write-Host "1/3 Removing old installation..." -ForegroundColor Yellow
    Start-Process -FilePath $OldUninst -ArgumentList "/S" -Wait
    Start-Sleep -Seconds 2
} else {
    Write-Host "Old install not found - skipping uninstall." -ForegroundColor DarkGray
}

if (-not (Test-Path $Installer)) {
    Write-Host "Installer missing. Building v$Version..." -ForegroundColor Yellow
    Set-Location $GuiRoot
    npm run electron:build
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

if (-not (Test-Path $Installer)) {
    Write-Host "ERROR: $Installer not found after build." -ForegroundColor Red
    Write-Host "For dev without reinstall, use: cd errorlogy-gui; npm run dev" -ForegroundColor Yellow
    exit 1
}

Write-Host "2/3 Installing Errorlogy $Version..." -ForegroundColor Green
Start-Process -FilePath $Installer -ArgumentList "/S" -Wait

if (Test-Path $Installed) {
    Write-Host "3/3 Done. Launch from Start Menu -> Errorlogy" -ForegroundColor Green
    Write-Host "  $Installed"

    $StartScript = Join-Path $GuiRoot "scripts\start-errorlogy.ps1"
    $Desktop = [Environment]::GetFolderPath("Desktop")
    $ShortcutPath = Join-Path $Desktop "Errorlogy.lnk"
    try {
        $WshShell = New-Object -ComObject WScript.Shell
        $Shortcut = $WshShell.CreateShortcut($ShortcutPath)
        $Shortcut.TargetPath = "powershell.exe"
        $Shortcut.Arguments = "-ExecutionPolicy Bypass -WindowStyle Hidden -File `"$StartScript`""
        $Shortcut.WorkingDirectory = $GuiRoot
        if (Test-Path $Installed) {
            $Shortcut.IconLocation = "$Installed,0"
        }
        $Shortcut.Description = "Errorlogy MAS API and GUI launcher"
        $Shortcut.Save()
        Write-Host "Desktop shortcut: $ShortcutPath" -ForegroundColor Green
        Write-Host "  (runs API preflight via start-errorlogy.ps1)" -ForegroundColor DarkGray
    } catch {
        Write-Host "Could not create desktop shortcut: $_" -ForegroundColor Yellow
    }
} else {
    Write-Host "Install may have failed - run installer manually:" -ForegroundColor Red
    Write-Host "  $Installer"
    exit 1
}
