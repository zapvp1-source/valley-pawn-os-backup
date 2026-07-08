# Stand down the not-yet-verified Bravo state guard so it can't spawn broken
# processes on a schedule. Leaves the WATCHER and its watchdog untouched.
foreach ($t in 'BravoStateGuard','ClaudeGuardOnce') {
    try { Stop-ScheduledTask -TaskName $t -ErrorAction SilentlyContinue } catch {}
    Unregister-ScheduledTask -TaskName $t -Confirm:$false -ErrorAction SilentlyContinue
    Write-Host ("unregistered task: " + $t)
}
# kill any lingering guard processes
Get-Process AutoHotkey64 -ErrorAction SilentlyContinue | ForEach-Object {
    $c = (Get-CimInstance Win32_Process -Filter "ProcessId=$($_.Id)").CommandLine
    if ($c -like '*bravo_state_guard.ahk*') { Write-Host ("killed guard PID=" + $_.Id); Stop-Process -Id $_.Id -Force }
}
# also clean the stale session-0 /validate zombies from prior sessions
Get-Process AutoHotkey64 -ErrorAction SilentlyContinue | ForEach-Object {
    $c = (Get-CimInstance Win32_Process -Filter "ProcessId=$($_.Id)").CommandLine
    if ($c -like '*/validate*') { Write-Host ("killed stale validate PID=" + $_.Id); Stop-Process -Id $_.Id -Force }
}
Start-Sleep 1
# report core pipeline health
Get-Process AutoHotkey64 -ErrorAction SilentlyContinue | ForEach-Object {
    $c = (Get-CimInstance Win32_Process -Filter "ProcessId=$($_.Id)").CommandLine
    if ($c -like '*bravo_watcher.ahk*')           { Write-Host ("WATCHER alive PID=" + $_.Id) }
    if ($c -like '*bravo_foreground_keeper.ahk*') { Write-Host ("FGKEEPER alive PID=" + $_.Id) }
}
Write-Host ("BravoWatcherWatchdog state: " + (Get-ScheduledTask -TaskName BravoWatcherWatchdog -ErrorAction SilentlyContinue).State)
Write-Host ("Bravo instances: " + ((Get-Process Bravo -ErrorAction SilentlyContinue) | Measure-Object).Count)
