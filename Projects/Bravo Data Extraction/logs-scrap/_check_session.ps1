Write-Output "=== interactive sessions ==="
try { query user 2>&1 | Out-String } catch { Write-Output "query user failed" }
Write-Output "=== explorer (interactive shell) ==="
Get-Process explorer -ErrorAction SilentlyContinue | Select-Object Id, SessionId | Format-List
Write-Output "=== dfsvc / clickonce ==="
Get-Process dfsvc -ErrorAction SilentlyContinue | Select-Object Id, SessionId | Format-List
Write-Output "=== ClaudeBravoClickOnce task result ==="
schtasks /query /tn ClaudeBravoClickOnce /fo LIST /v 2>&1 | Select-String "Last Run|Last Result|Status"
