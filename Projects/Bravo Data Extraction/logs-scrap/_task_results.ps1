foreach ($t in @('ClaudeBravoSelfHeal','ClBravoDirect','ClaudeBravoAppRef','BravoWatcherWatchdog')) {
    Write-Output "=== $t ==="
    schtasks /query /tn $t /fo LIST /v 2>&1 | Select-String "Last Run Time|Last Result|Scheduled Task State|Logon Mode"
}
Write-Output "=== pipeline output freshness (newest 8) ==="
Get-ChildItem '\\Mac\Home\Documents\Claude\Projects\Bravo Data Extraction\output' -Filter *.csv |
    Sort-Object LastWriteTime -Descending | Select-Object -First 8 Name, LastWriteTime | Format-Table -AutoSize | Out-String
