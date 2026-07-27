# Bravo Password Rotation Runbook

Bravo uses ONE universal login for all 5 stores: username `FREE1@WAY`.
When the password changes, update it in these places, then restart the watcher.

## Primary (AHK production path — the live watcher + all report handlers)
1. `lib/_secrets.ahk` — the ONE line `BRAVO_PASSWORD := "..."`. This is the
   single source of truth for `bravo_watcher.ahk` and `bravo_export.ahk`.
   (Those two files keep a literal fallback only so the watcher can still boot
   if the include is ever missing — update the fallback too if you touch it.)

## Secondary (independent login mechanisms — keep in sync)
2. `config.json` -> `bravo.password` — read by `_selfheal.ahk`, `nics_*.ahk`.
3. PowerShell logins (older, still present):
   - `_bravo_login.ps1`, `_bravo_session.ps1` (this folder)
   - `../Daily Funds Verification/_bravo_login.ps1`, `_bravo_session.ps1`

## After editing
- Run `_restart_watcher.ps1` so the running watcher reloads the new value.
- Verify: no old password remains anywhere:
    grep -rIl 'OLDVALUE' ~/Documents/Claude/Projects

## Skills (updated separately in Claude Settings > Capabilities, not on disk)
- `bravo-context` -> Authentication section
- `bravo-store-cycle` -> Credentials + step 5 + troubleshooting

Last rotation: 2026-07-17 -> Health2080!

## Guest-side (Windows VM C: drive - edit via prlctl/RDP)
4. BravoAutoLogin.ahk in the Windows Startup folder runs at login and performs the initial Bravo login. Self-contained BRAVO_PASSWORD literal (kept local because Y: may not be mapped at boot). Found via the running AutoHotkey64 process list, not the Mac grep.

---

## Fastest path - the rotate-bravo-password skill
Do not do these steps by hand unless you have to. Just tell Claude: rotate the Bravo password to NEWVALUE (or: the Bravo password changed to NEWVALUE). The rotate-bravo-password skill runs this entire runbook autonomously - auto-detects the current password, backs up, sweeps all Mac-side files, fixes the guest-side BravoAutoLogin.ahk in the Windows VM, restarts the watcher and confirms it is back up on the Y: path, verifies zero drift, and repackages the bravo-context and bravo-store-cycle skill bundles to save. This document is the manual fallback if that skill is ever unavailable.
