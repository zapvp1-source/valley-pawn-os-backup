Write-Output "=== Application log, last 30 min, all levels ==="
Get-WinEvent -FilterHashtable @{LogName='Application'; StartTime=(Get-Date).AddMinutes(-30)} -ErrorAction SilentlyContinue |
    Select-Object -First 12 TimeCreated, LevelDisplayName, ProviderName,
        @{n='Msg';e={($_.Message -replace "`r`n",' ').Substring(0,[Math]::Min(160,$_.Message.Length))}} |
    Format-List | Out-String
Write-Output "=== VM display / session ==="
query user 2>&1 | Out-String
