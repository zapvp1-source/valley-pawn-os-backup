$root = 'Y:\Documents\Claude\Projects\Bravo Data Extraction'
if (-not (Test-Path $root)) { $root = '\\Mac\Home\Documents\Claude\Projects\Bravo Data Extraction' }
# kill any running guard
Get-Process AutoHotkey64 -ErrorAction SilentlyContinue | ForEach-Object {
    $c = (Get-CimInstance Win32_Process -Filter "ProcessId=$($_.Id)").CommandLine
    if ($c -like '*bravo_state_guard.ahk*') { Write-Host ("killed guard PID=" + $_.Id); Stop-Process -Id $_.Id -Force }
}
# remove the one-shot task
Unregister-ScheduledTask -TaskName 'ClaudeGuardOnce' -Confirm:$false -ErrorAction SilentlyContinue
# report watcher + foreground keeper health
Get-Process AutoHotkey64 -ErrorAction SilentlyContinue | ForEach-Object {
    $c = (Get-CimInstance Win32_Process -Filter "ProcessId=$($_.Id)").CommandLine
    if ($c -like '*bravo_watcher.ahk*')          { Write-Host ("watcher ALIVE PID=" + $_.Id + " Sess=" + $_.SessionId) }
    if ($c -like '*bravo_foreground_keeper.ahk*'){ Write-Host ("fgkeeper ALIVE PID=" + $_.Id + " Sess=" + $_.SessionId) }
}
$bravo = Get-Process Bravo -ErrorAction SilentlyContinue
Write-Host ("Bravo instances: " + ($bravo | Measure-Object).Count)
