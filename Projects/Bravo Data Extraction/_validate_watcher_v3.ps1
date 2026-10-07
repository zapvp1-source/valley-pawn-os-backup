# _validate_watcher_v3.ps1 - added 2026-10-06 (jewelry v3). Syntax/load-validates bravo_watcher.ahk
# with AutoHotkey /validate WITHOUT restarting anything. Writes logs\_validate_watcher_v3.txt:
#   VAL exit=<n> then any AHK error text. exit=0 means the script loads cleanly.
$base = "Y:\Documents\Claude\Projects\Bravo Data Extraction"
$ahk  = "C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe"
$out  = Join-Path $base "logs\_validate_watcher_v3.txt"
$err  = Join-Path $env:TEMP "vp_validate_v3_err.txt"
Set-Content -Path $out -Value ("VSTART " + (Get-Date -Format o)) -Encoding utf8
$script = Join-Path $base "bravo_watcher.ahk"
$p = Start-Process -FilePath $ahk -ArgumentList @("/ErrorStdOut", "/validate", ('"' + $script + '"')) -Wait -PassThru -WindowStyle Hidden -RedirectStandardError $err -RedirectStandardOutput ($err + ".out")
Add-Content -Path $out -Value ("VAL exit=" + $p.ExitCode) -Encoding utf8
if (Test-Path $err) { Get-Content $err | Add-Content -Path $out -Encoding utf8 }
if (Test-Path ($err + ".out")) { Get-Content ($err + ".out") | Add-Content -Path $out -Encoding utf8 }
Add-Content -Path $out -Value ("VDONE " + (Get-Date -Format o)) -Encoding utf8
Write-Host ("VAL exit=" + $p.ExitCode)
