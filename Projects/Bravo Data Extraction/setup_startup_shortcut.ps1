# Creates a Windows Startup shortcut that launches bravo_watcher.ahk
# Run inside the VM. Idempotent — overwrites the .lnk if it already exists.

$ErrorActionPreference = 'Stop'

$ahkExe   = 'C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe'
$ahkExeAlt = 'C:\Program Files\AutoHotkey\AutoHotkey64.exe'
$watcher  = 'Y:\Documents\Claude\Projects\Bravo Data Extraction\bravo_watcher.ahk'
$startup  = [System.Environment]::GetFolderPath('Startup')
$lnkPath  = Join-Path $startup 'BravoWatcher.lnk'

# Find the AutoHotkey executable
$exePath = $null
if (Test-Path $ahkExe) {
    $exePath = $ahkExe
} elseif (Test-Path $ahkExeAlt) {
    $exePath = $ahkExeAlt
} else {
    # Search Program Files for AutoHotkey64.exe under any AutoHotkey* folder
    $found = Get-ChildItem 'C:\Program Files\AutoHotkey*' -Recurse -Filter 'AutoHotkey64.exe' -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($found) { $exePath = $found.FullName }
}

if (-not $exePath) {
    Write-Host "ERROR: AutoHotkey64.exe not found under C:\Program Files\AutoHotkey*"
    Write-Host "Please install AutoHotkey v2 or set the path manually."
    exit 1
}

Write-Host "AutoHotkey exe:   $exePath"
Write-Host "Watcher script:   $watcher"
Write-Host "Startup shortcut: $lnkPath"

if (-not (Test-Path $watcher)) {
    Write-Host "ERROR: watcher script not found at $watcher"
    exit 1
}

$wsh = New-Object -ComObject WScript.Shell
$lnk = $wsh.CreateShortcut($lnkPath)
$lnk.TargetPath       = $exePath
$lnk.Arguments        = "`"$watcher`""
$lnk.WorkingDirectory = (Split-Path $watcher -Parent)
$lnk.Description      = 'Bravo Data Extraction watcher'
$lnk.WindowStyle      = 7  # Minimized
$lnk.IconLocation     = "$exePath, 0"
$lnk.Save()

Write-Host ""
Write-Host "Created: $lnkPath"
Write-Host "It will auto-launch the watcher on every Windows login."
Write-Host ""
Write-Host "To test now without logging out:"
Write-Host "  & '$exePath' '$watcher'"
