# 2026-08-10: restore the normal Bravo self-heal chain after a session where
# PauseMainWatcher's blanket AutoHotkey64 kill took out BravoAutoLogin.ahk and
# bravo_foreground_keeper.ahk (not just the main watcher). Those two are what
# relaunch Bravo via ClickOnce and drive the login screen; without them Bravo
# cannot come back on its own.
Get-Process Bravo -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 3

$ahk = 'C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe'
$jobs = @(
  @{ n='ClaudeRestoreAutoLogin'; s='C:\Users\joshuadavis\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\BravoAutoLogin.ahk' },
  @{ n='ClaudeRestoreKeeper';    s='Y:\Documents\Claude\Projects\Bravo Data Extraction\bravo_foreground_keeper.ahk' }
)
$p = New-ScheduledTaskPrincipal -UserId 'joshuadavis' -LogonType Interactive
$s = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
foreach ($j in $jobs) {
    Unregister-ScheduledTask -TaskName $j.n -Confirm:$false -ErrorAction SilentlyContinue
    $a = New-ScheduledTaskAction -Execute $ahk -Argument ('"' + $j.s + '"')
    Register-ScheduledTask -TaskName $j.n -Action $a -Principal $p -Settings $s -Force | Out-Null
    Start-ScheduledTask -TaskName $j.n
    Write-Output ("started: " + $j.n)
}
schtasks /run /tn BravoWatcherWatchdog 2>&1 | Out-Null
Write-Output "watchdog kicked"
