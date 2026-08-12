# Pause the scrap-closeout system for this work session (reversible).
# 1) disable + end the Windows watchdog task that relaunches the scrap watcher
# 2) stop any running scrap watcher AHK process
$out = '\\Mac\Home\Documents\Claude\Projects\Bravo Data Extraction\logs\_scrap_pause_result.txt'
$r = @()
try {
    schtasks /change /tn "ScrapCloseoutWatcherWatchdog" /disable 2>&1 | Out-Null
    schtasks /end     /tn "ScrapCloseoutWatcherWatchdog" 2>&1 | Out-Null
    $r += "watchdog task: disabled + ended"
} catch { $r += "watchdog task err: $($_.Exception.Message)" }

$killed = 0
Get-Process AutoHotkey64 -ErrorAction SilentlyContinue | ForEach-Object {
    $cmd = ""
    try { $cmd = (Get-CimInstance Win32_Process -Filter "ProcessId=$($_.Id)").CommandLine } catch {}
    if ($cmd -like '*ScrapBucketCloseoutWatcher*' -or $cmd -like '*scrap*' -or $cmd -like '*Scrap*') {
        try { Stop-Process -Id $_.Id -Force; $killed++; $r += "killed AHK pid $($_.Id)" } catch {}
    }
}
$r += "scrap AHK procs killed: $killed"
$r -join "`r`n" | Set-Content $out
Write-Host ($r -join ' | ')
