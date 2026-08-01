# Launch Bravo via the ClickOnce shim in the interactive Session 1.
# cmd /c start "" <appref-ms> silently fails through prlctl (quoting).
# rundll32 dfshim.dll,ShOpenVerbShortcut is the supported ClickOnce launcher.
$ErrorActionPreference = 'Continue'
$user = "joshuadavis"
$shortcut = "C:\Users\joshuadavis\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Bravo Store Systems\Bravo.appref-ms"

Unregister-ScheduledTask -TaskName ClaudeBravoClickOnce -Confirm:$false -ErrorAction SilentlyContinue
$a = New-ScheduledTaskAction -Execute 'rundll32.exe' -Argument ("dfshim.dll,ShOpenVerbShortcut " + $shortcut)
$t = New-ScheduledTaskTrigger -Once -At ((Get-Date).AddYears(10))
$p = New-ScheduledTaskPrincipal -UserId $user -LogonType Interactive -RunLevel Limited
$s = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName ClaudeBravoClickOnce -Action $a -Trigger $t -Principal $p -Settings $s -Force | Out-Null
Start-ScheduledTask -TaskName ClaudeBravoClickOnce
Start-Sleep -Seconds 40
Unregister-ScheduledTask -TaskName ClaudeBravoClickOnce -Confirm:$false -ErrorAction SilentlyContinue

$b = Get-Process -Name "Bravo*" -ErrorAction SilentlyContinue
if ($b) { foreach ($x in $b) { Write-Host ("BRAVO PID=" + $x.Id + " Session=" + $x.SessionId) } }
else { Write-Host "BRAVO NOT RUNNING" }
