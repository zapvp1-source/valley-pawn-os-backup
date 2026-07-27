# Install the Bravo Readiness Keeper: add a Startup shortcut (runs at login) AND
# start it now in the interactive Session 1 via the scheduled-task spawn trick.
$ErrorActionPreference = 'Continue'
$ahk    = "C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe"
$keeper = "Y:\Documents\Claude\Projects\Bravo Data Extraction\bravo_foreground_keeper.ahk"
$root   = "Y:\Documents\Claude\Projects\Bravo Data Extraction"

# 1. Startup shortcut so it relaunches every login (same pattern as the watcher)
$startup = [Environment]::GetFolderPath('Startup')
$lnk = Join-Path $startup 'BravoForegroundKeeper.lnk'
$wsh = New-Object -ComObject WScript.Shell
$sc = $wsh.CreateShortcut($lnk)
$sc.TargetPath = $ahk
$sc.Arguments = '"' + $keeper + '"'
$sc.WorkingDirectory = $root
$sc.Save()
Write-Host "Startup shortcut: $lnk"

# 2. Start now in Session 1 (prlctl runs us in Session 0; scheduled-task trick hops to S1)
$taskName = "ClaudeKeeperLaunch"
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
$action    = New-ScheduledTaskAction -Execute $ahk -Argument ('"' + $keeper + '"')
$trigger   = New-ScheduledTaskTrigger -Once -At ((Get-Date).AddYears(10))
$principal = New-ScheduledTaskPrincipal -UserId "joshuadavis" -LogonType Interactive -RunLevel Limited
$settings  = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null
Start-ScheduledTask -TaskName $taskName
Start-Sleep -Seconds 5
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue

# 3. Verify it's running
$found = $false
Get-Process AutoHotkey64 -ErrorAction SilentlyContinue | ForEach-Object {
    $cmd = (Get-CimInstance Win32_Process -Filter "ProcessId=$($_.Id)").CommandLine
    if ($cmd -like "*bravo_foreground_keeper*") { $found = $true; Write-Host ("Keeper RUNNING PID=" + $_.Id + " Session=" + $_.SessionId) }
}
if (-not $found) { Write-Host "WARN: keeper process not detected yet" }
Write-Host "=== install done ==="
