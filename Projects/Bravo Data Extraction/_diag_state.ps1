$diag = @()
$diag += "=== $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') diagnostic ==="
$diag += "whoami: $(whoami)"
$diag += "---drives---"
$diag += (Get-PSDrive -PSProvider FileSystem | Out-String)
$diag += "---Y: config.json test---"
if (Test-Path 'Y:\Documents\Claude\Projects\Bravo Data Extraction\config.json') {
    $diag += "Y: config.json VISIBLE"
} else {
    $diag += "Y: config.json NOT visible"
}
$diag += "---Bravo processes---"
$diag += (Get-Process Bravo*,AutoHotkey* -ErrorAction SilentlyContinue | Select-Object Id,ProcessName,Responding,StartTime,MainWindowTitle | Out-String)
$diag -join "`n" | Out-File C:\Users\Public\diag_state.txt
