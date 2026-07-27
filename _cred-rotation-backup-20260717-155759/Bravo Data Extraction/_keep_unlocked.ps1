# _keep_unlocked.ps1 — stop the Windows VM from locking / showing the sign-in screen.
# Writes a result log the Mac side can read.
$out = "Y:\Documents\Claude\Projects\Bravo Data Extraction\_keep_unlocked_result.txt"
"START $(Get-Date -Format o)" | Out-File $out -Encoding utf8
function L($m){ $m | Out-File $out -Append -Encoding utf8 }

# 1. Disable the screensaver AND its 'show logon on resume' (per-user, no admin)
L (reg add "HKCU\Control Panel\Desktop" /v ScreenSaveActive   /t REG_SZ /d 0 /f 2>&1)
L (reg add "HKCU\Control Panel\Desktop" /v ScreenSaverIsSecure /t REG_SZ /d 0 /f 2>&1)
L (reg add "HKCU\Control Panel\Desktop" /v ScreenSaveTimeOut   /t REG_SZ /d 0 /f 2>&1)

# 2. Never turn off the display, never sleep (AC + DC)
L (powercfg /change monitor-timeout-ac 0 2>&1)
L (powercfg /change monitor-timeout-dc 0 2>&1)
L (powercfg /change standby-timeout-ac 0 2>&1)
L (powercfg /change standby-timeout-dc 0 2>&1)

# 3. Do NOT require a password on wake (CONSOLELOCK = 0)
L (powercfg /SETACVALUEINDEX SCHEME_CURRENT SUB_NONE 0e796bdb-100d-47d6-a2d5-f7d2daa51f51 0 2>&1)
L (powercfg /SETDCVALUEINDEX SCHEME_CURRENT SUB_NONE 0e796bdb-100d-47d6-a2d5-f7d2daa51f51 0 2>&1)
L (powercfg /SETACTIVE SCHEME_CURRENT 2>&1)

# 4. Machine inactivity limit = 0 (no idle auto-lock).  HKLM => needs admin; try anyway.
L (reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" /v InactivityTimeoutSecs /t REG_DWORD /d 0 /f 2>&1)

# 5. Turn off the lock screen entirely.  HKLM => needs admin; try anyway.
L (reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\Personalization" /v NoLockScreen /t REG_DWORD /d 1 /f 2>&1)

# Report effective state
L "--- verify ---"
L (reg query "HKCU\Control Panel\Desktop" /v ScreenSaverIsSecure 2>&1)
L (reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" /v InactivityTimeoutSecs 2>&1)
L "DONE $(Get-Date -Format o)"
