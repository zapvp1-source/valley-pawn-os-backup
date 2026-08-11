# Launch Bravo from the CURRENT ClickOnce cache build, in interactive Session 1.
# 2026-08-10: ClBravoDirect was failing with 0x80070002 (file not found) because
# it holds a hardcoded cache path from an older Bravo build; the ClickOnce cache
# directory name changes on every Bravo update. This resolves the newest
# Bravo.exe at run time instead of trusting a stale path.
$exe = Get-ChildItem "C:\Users\joshuadavis\AppData\Local\Apps\2.0" -Recurse -Filter 'Bravo.exe' -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTime -Descending | Select-Object -First 1
if (-not $exe) { Write-Output "NO BRAVO.EXE FOUND"; exit 1 }
Write-Output ("using: " + $exe.FullName)

$taskName = 'ClaudeBravoLaunchNow'
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
$a = New-ScheduledTaskAction -Execute $exe.FullName -WorkingDirectory $exe.DirectoryName
$p = New-ScheduledTaskPrincipal -UserId 'joshuadavis' -LogonType Interactive
$s = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName $taskName -Action $a -Principal $p -Settings $s -Force | Out-Null
Start-ScheduledTask -TaskName $taskName
Write-Output "LAUNCH REQUESTED"
