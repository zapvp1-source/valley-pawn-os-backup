Write-Output "--- watchdog task state ---"
schtasks /query /tn ScrapCloseoutWatcherWatchdog /fo LIST | Select-String "Status|TaskName|Scheduled Task State"
Write-Output "--- killing scrap closeout watcher only ---"
Get-WmiObject Win32_Process -Filter "Name='AutoHotkey64.exe'" | ForEach-Object {
    if ($_.CommandLine -like "*ScrapBucketCloseoutWatcher*") {
        Write-Output ("killing scrap watcher PID " + $_.ProcessId)
        Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
    }
}
Start-Sleep -Seconds 2
Write-Output "--- remaining AHK processes ---"
Get-WmiObject Win32_Process -Filter "Name='AutoHotkey64.exe'" | Select-Object ProcessId, CommandLine | Format-List
