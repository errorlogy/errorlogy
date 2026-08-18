# Errorlogy — create Start Menu + Desktop shortcuts after NSIS install
# Run this if the NSIS installer was not used (e.g. using the dir build)

$AppName    = "Errorlogy"
$BuildDir   = "$PSScriptRoot\dist-electron\win-unpacked"
$InstallDir = "$env:LOCALAPPDATA\Programs\Errorlogy"
$ExePath    = "$InstallDir\Errorlogy.exe"
$IconPath   = "$InstallDir\Errorlogy.exe"

# 1 — Copy unpacked build to a permanent install location
Write-Host "Copying app to $InstallDir ..."
if (Test-Path $InstallDir) { Remove-Item $InstallDir -Recurse -Force }
Copy-Item $BuildDir $InstallDir -Recurse -Force
Write-Host "App installed."

# 2 — Start Menu shortcut
$StartMenu = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs"
$WS = New-Object -ComObject WScript.Shell
$ShortcutSM = $WS.CreateShortcut("$StartMenu\$AppName.lnk")
$ShortcutSM.TargetPath   = $ExePath
$ShortcutSM.WorkingDirectory = $InstallDir
$ShortcutSM.Description  = "Errorlogy MAS — Government Error Analysis"
$ShortcutSM.IconLocation = "$IconPath,0"
$ShortcutSM.Save()
Write-Host "Start Menu shortcut created: $StartMenu\$AppName.lnk"

# 3 — Desktop shortcut
$Desktop = [Environment]::GetFolderPath("Desktop")
$ShortcutD = $WS.CreateShortcut("$Desktop\$AppName.lnk")
$ShortcutD.TargetPath    = $ExePath
$ShortcutD.WorkingDirectory = $InstallDir
$ShortcutD.Description   = "Errorlogy MAS — Government Error Analysis"
$ShortcutD.IconLocation  = "$IconPath,0"
$ShortcutD.Save()
Write-Host "Desktop shortcut created: $Desktop\$AppName.lnk"

Write-Host ""
Write-Host "Done! Launch Errorlogy from Start Menu or Desktop."
