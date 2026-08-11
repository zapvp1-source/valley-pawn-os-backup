Write-Output "=== all processes named like bravo/dfsvc/rundll ==="
Get-Process | Where-Object { $_.ProcessName -match 'ravo|dfsvc|rundll32|AutoHotkey' } | Select-Object Id, ProcessName, SessionId | Format-Table -AutoSize | Out-String

Write-Output "=== ClickOnce cache newest Bravo.exe ==="
$base = "C:\Users\joshuadavis\AppData\Local\Apps\2.0"
if (Test-Path $base) {
    Get-ChildItem $base -Recurse -Filter 'Bravo.exe' -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending | Select-Object -First 3 FullName, LastWriteTime |
        Format-List | Out-String
} else { Write-Output "no ClickOnce cache at $base" }

Write-Output "=== recent Application-log errors (last 24h) ==="
Get-WinEvent -FilterHashtable @{LogName='Application'; StartTime=(Get-Date).AddHours(-24)} -ErrorAction SilentlyContinue |
    Where-Object { $_.LevelDisplayName -eq 'Error' } |
    Select-Object -First 8 TimeCreated, ProviderName, @{n='Msg';e={$_.Message.Substring(0,[Math]::Min(200,$_.Message.Length))}} |
    Format-List | Out-String
