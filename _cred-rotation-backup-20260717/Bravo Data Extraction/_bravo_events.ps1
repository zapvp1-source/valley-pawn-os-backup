# _bravo_events.ps1 — recent app errors + ClickOnce launch attempt with visible output
$out = '\\Mac\Home\Documents\Claude\Projects\Bravo Data Extraction\logs\_bravo_events.txt'
"=== Application errors last 2h ===" | Set-Content $out
Get-WinEvent -FilterHashtable @{LogName='Application'; Level=2; StartTime=(Get-Date).AddHours(-2)} -MaxEvents 20 -ErrorAction SilentlyContinue |
    ForEach-Object { ($_.TimeCreated.ToString('HH:mm:ss') + ' [' + $_.ProviderName + '] ' + ($_.Message -replace "`r`n",' | ').Substring(0, [Math]::Min(400, $_.Message.Length))) } |
    Add-Content $out
"=== dfsvc / Bravo processes ===" | Add-Content $out
Get-Process -Name 'Bravo*','dfsvc' -ErrorAction SilentlyContinue |
    ForEach-Object { ('PROC ' + $_.ProcessName + ' PID=' + $_.Id + ' Session=' + $_.SessionId) } | Add-Content $out
"done" | Add-Content $out
