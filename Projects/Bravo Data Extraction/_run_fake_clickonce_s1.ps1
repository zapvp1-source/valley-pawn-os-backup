# Launch the fake ClickOnce test dialog in interactive Session 1 (prlctl runs us
# in Session 0; the scheduled-task trick hops to S1 so the GUI is visible to the
# keeper). TEST ONLY — removes its own scheduled task afterward.
$ahk    = "C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe"
$script = "Y:\Documents\Claude\Projects\Bravo Data Extraction\_test_fake_clickonce.ahk"
$taskName = "ClaudeFakeClickOnceTest"

$action    = New-ScheduledTaskAction -Execute $ahk -Argument ('"' + $script + '"')
$principal = New-ScheduledTaskPrincipal -UserId "joshuadavis" -LogonType Interactive -RunLevel Limited
$settings  = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName $taskName -Action $action -Principal $principal -Settings $settings -Force | Out-Null
Start-ScheduledTask -TaskName $taskName
Start-Sleep -Seconds 3
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
Write-Host "fake-clickonce test dialog launched in Session 1"
