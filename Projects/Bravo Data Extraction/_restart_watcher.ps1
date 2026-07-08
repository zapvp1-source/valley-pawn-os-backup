# _restart_watcher.ps1 — relaunches the AHK watcher in joshuadavis's
# interactive session with Y: drive mapped first.
#
# Why Y:: the watcher derives output paths from its launch directory
# (bravo_watcher.ahk line 98: paths.output := SCRIPT_DIR . "\output").
# If launched from \\Mac\Home\..., handlers pass UNC paths to Bravo's
# Export Document dialog. UNC SMB over Parallels Shared Folders is
# slow enough that EOM CSV writes that take ~5s on Y: take >180s on
# UNC — every cell times out. Launching from Y:\... keeps everything
# on the mapped-drive fast path.
#
# Modified 2026-05-29 to map Y: in joshuadavis session before launch.

# --- Step 1: kill any existing watchers (UNC- or Y:-launched) -----------
Get-Process AutoHotkey64 -ErrorAction SilentlyContinue | Where-Object {
    $cmd = (Get-WmiObject Win32_Process -Filter "ProcessId=$($_.Id)").CommandLine
    $cmd -like "*bravo_watcher.ahk*"
} | ForEach-Object {
    Write-Host ("Stopping watcher PID=" + $_.Id)
    Stop-Process -Id $_.Id -Force
}
Start-Sleep -Seconds 2

# --- Step 2: ensure Y: is mapped persistently in joshuadavis's session --
# Without this, AHK launched from Y: path fails immediately if Y: isn't
# present in joshuadavis's drive table (per-user, per-session mapping).
$mapTaskName = "ClaudeMapYDrive"
Unregister-ScheduledTask -TaskName $mapTaskName -Confirm:$false -ErrorAction SilentlyContinue
$mapAction    = New-ScheduledTaskAction -Execute 'cmd.exe' -Argument '/c net use Y: \\Mac\Home /persistent:yes'
$mapTrigger   = New-ScheduledTaskTrigger -Once -At ((Get-Date).AddYears(10))
$mapPrincipal = New-ScheduledTaskPrincipal -UserId "joshuadavis" -LogonType Interactive -RunLevel Limited
$mapSettings  = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName $mapTaskName -Action $mapAction -Trigger $mapTrigger -Principal $mapPrincipal -Settings $mapSettings -Force | Out-Null
Start-ScheduledTask -TaskName $mapTaskName
Start-Sleep -Seconds 4
Unregister-ScheduledTask -TaskName $mapTaskName -Confirm:$false -ErrorAction SilentlyContinue
Write-Host "Y: drive net-use issued in joshuadavis session"

# --- Step 3: launch watcher with Y: path so SCRIPT_DIR resolves Y: ------
$taskName = "ClaudeBravoWatcherLaunch2"
$ahk      = "C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe"
$watcher  = '"Y:\Documents\Claude\Projects\Bravo Data Extraction\bravo_watcher.ahk"'

Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue

$action    = New-ScheduledTaskAction -Execute $ahk -Argument $watcher
$trigger   = New-ScheduledTaskTrigger -Once -At ((Get-Date).AddYears(10))
$principal = New-ScheduledTaskPrincipal -UserId "joshuadavis" -LogonType Interactive -RunLevel Limited
$settings  = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null
Start-ScheduledTask -TaskName $taskName
Start-Sleep -Seconds 6

# --- Step 4: verify ------------------------------------------------------
$found = $false
Get-Process AutoHotkey64 -ErrorAction SilentlyContinue | ForEach-Object {
    $cmd = (Get-WmiObject Win32_Process -Filter "ProcessId=$($_.Id)").CommandLine
    if ($cmd -like "*bravo_watcher.ahk*") {
        $found = $true
        Write-Host ("PID=" + $_.Id + " Session=" + $_.SessionId + " CMD=" + $cmd)
        if ($cmd -notlike "*Y:\Documents*") {
            Write-Host "WARN: watcher launched but NOT using Y: path - paths will be slow UNC"
        }
    }
}
if (-not $found) {
    Write-Host "ERROR: watcher did not start. Y: may not be mapped in joshuadavis session - sign out/in or check net use Y:"
}

Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
Write-Host "Watcher restart complete (Y:-path version, 2026-05-29)"
