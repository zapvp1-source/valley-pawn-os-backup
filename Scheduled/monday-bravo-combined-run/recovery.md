# Bravo Watcher Hang Recovery — runbook

Recovery procedure when the `bravo_watcher.ahk` AutoHotkey script inside the
Parallels Windows 11 VM hangs mid-trigger. This is automation Claude executes
autonomously when a hang is detected — Joshua does not need to be present.

## When this runbook applies

A hang means: a trigger has been dropped, the watcher started processing it
(CSVs appearing in `output/`), but then progress stopped. Specifically:

- The watcher log `logs/<trigger-id>.log` has not been written to for 3+ minutes
- No `results/<trigger-id>.result.json` has appeared
- The trigger JSON is still in `triggers/<id>.json` (not yet moved to `processed/`)

If CSVs are still appearing or the result JSON is present, this is NOT a hang.

## Constants

- VM UUID: `{7dc84f03-4e68-4f43-9596-bf8a7dfb8e0a}` (Parallels "Windows 11")
- prlctl path: `/usr/local/bin/prlctl`
- Project root: `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/`
- VM-side mount: `Y:\Documents\Claude\Projects\Bravo Data Extraction\`
- Watcher launcher: `start_watcher.bat` at the project root (executes AutoHotkey64.exe with bravo_watcher.ahk)
- Joshua Slack DM: `U03BB52MDSA`

## Watcher safety rails (added 2026-05-13)

The `bravo_watcher.ahk` `ProcessTrigger` loop has two trip conditions that short-circuit a run before it can do damage. These are pure orchestration logic — no Bravo UI interaction — and they prevent the kind of lockout cascade that happened on 2026-05-13:

**1. Auth-failure circuit breaker.** Tracks consecutive cells whose result reports `EnsureStore failed`. After `MAX_CONSECUTIVE_AUTH_FAILURES` in a row (default `3`, configurable via `config.json` key `watcher.max_consecutive_auth_failures`), the watcher stops processing the rest of the trigger. Remaining cells are written to `result.json` as `status: "skipped"` with `error: "Skipped by safety rail: auth-failure circuit breaker (...)"`. The trigger is moved to `processed/` so the orchestrator sees a result. Any successful cell resets the counter to zero — a single transient EnsureStore failure won't trip the breaker.

**2. Per-trigger hard-wall timeout.** A wall-clock check before each cell. If elapsed time since the trigger started exceeds `MAX_TRIGGER_DURATION_MS` (default `2,700,000` = 45 min, configurable via `watcher.max_trigger_duration_ms`), the watcher stops dispatching cells and marks the remainder skipped with `error: "Skipped by safety rail: hard-wall-timeout (>2700s elapsed)"`. This catches the case where a single cell hangs inside a blocking UIA call.

**What the orchestrator should do when it sees safety-rail trips:**
- `status: "aborted"` in the result.json — read the first skipped cell's `error` field for the reason.
- If it's the auth-failure breaker: do NOT auto-drop a follow-up trigger. Authentication is broken, and dropping a follow-up just makes things worse (today's lockout was caused by exactly this). DM Joshua with the failure reason and stop.
- If it's the hard-wall timeout: the watcher is alive but a cell is hung. Apply the standard hang-recovery (kill + restart watcher, move stuck trigger, optionally drop a follow-up for the cells that didn't get to run).

**Tuning the thresholds:** edit `config.json` keys `watcher.max_consecutive_auth_failures` (integer) and `watcher.max_trigger_duration_ms` (integer milliseconds). Restart the watcher to pick up new values.

**To disable the safety rails entirely** (not recommended): set the thresholds to absurdly high values (e.g., `9999` failures, `999999999` ms). The original 2026-05-12 backup is preserved at `bravo_watcher.ahk.bak-2026-05-13` if a full rollback is ever needed.

## STANDING RULE — never logout, always Lock Session

(Added 2026-05-13 by Joshua.) The watcher must NEVER click "End Session" or otherwise terminate a Bravo user's session. Always use "Lock Session" when leaving a store and "Resume Session" when arriving at one that already has an active session. Locking preserves the user's session — most importantly, it preserves whatever User Name is pre-filled on the Login form when you Resume. Ending the session destroys both, which means when you later return to that store you land on a Login form whose User Name pre-fill is unpredictable (often whoever the system thinks "last" interacted with that store).

This rule is enforced in two places:

1. `lib/StoreCycle.ahk` post-row Session List handler (the screen that appears after dblclicking a store): the click ladder is `Resume Session -> New User`. **`End Session` is explicitly NOT in the ladder.** If both Resume and New User fail, the cell fails and the watcher's circuit breaker handles it.

2. The "Lock Session" step earlier in `SwitchStore` is unchanged — that's the correct action when leaving a store, and it's what makes Resume Session viable at the destination.

The wrong-username problem (Login form pre-filled with someone other than FREE1@WAY after Resume Session) is solved separately by the failsafe rule below, not by destroying sessions.

## STANDING RULE — Step 5 username failsafe (Switch User -> New User)

(Added 2026-05-13 by Joshua.) After the Login form renders — regardless of whether we got there via the Submit-direct path, Resume Session, or New User — the watcher must verify the User Name field shows FREE1@WAY before typing any credentials. If it shows anything else (and is not empty), the watcher must:

1. Click `Switch User` to back out to the Session List.
2. Click `New User` on the Session List to land on a fresh empty Login form.
3. Fall into the existing `cameFromNewUser` explicit-fill path which clicks the User Name field by name and pastes FREE1@WAY via clipboard.
4. Then type the password and submit normally.

This rule is enforced in:
- `lib/StoreCycle.ahk` Step 5 (around line 220, just before the existing `if cameFromNewUser` block).
- `lib/Bravo.ahk` RecoverFromAutoLock (around line 357, just before the password-field find block).

The read of the User Name field uses UIA `Value` and is read-only — it cannot corrupt anything. The Switch User / New User actions use `ClickByName` which has built-in retry and visual click logic. The explicit-fill keystroke sequence runs only after a fresh empty form is confirmed, so there's no risk of keystrokes landing in the wrong field. This is the **safe** replacement for the 2026-05-13 morning patch that locked the account by blindly typing into the password field.

Why this matters: submitting FREE1's password against any other username silently fails authentication. With the watcher's auth-failure circuit breaker armed at N=3, three of these in a row aborts the trigger, but a third strike against an account that's already had failed attempts will lock it. Resetting via the Switch User path means we never submit wrong-username credentials.

## STANDING RULE — per-store username override (WAY uses `FREE1`, others `FREE1@WAY`)

(Added 2026-05-13 by Joshua.) The FREE1 service account is *based out of* Waynesboro. At the WAY store the User Name field expects just `FREE1` with no `@WAY` suffix — the suffix is implicit because the account is local to that store. At all four other stores (CUL, HAR, LEX, ROA) the canonical username is `FREE1@WAY`.

Wherever the watcher computes the expected/typed username, it must check `targetStore` (in `SwitchStore`) or `GetCurrentStoreCode()` (in `RecoverFromAutoLock`) and use the WAY-specific form when at WAY:

```ahk
expectedUser := CONFIG.Has("bravo.username") ? CONFIG["bravo.username"] : "FREE1@WAY"
if (targetStore = "WAY")
    expectedUser := "FREE1"
```

This is enforced in three code locations as of 2026-05-13:
- `lib/StoreCycle.ahk` Step 5 failsafe — `expectedUser` for the read-and-compare check.
- `lib/StoreCycle.ahk` existing `cameFromNewUser` fill block — `username` for the explicit paste.
- `lib/Bravo.ahk` `RecoverFromAutoLock` failsafe — `autoLockExpectedUser` (current store read from title bar).

The Step 5 failsafe rule still holds: if the rendered Login form pre-fill is anything other than the *expected per-store* username, click Switch User → New User and re-fill. At WAY this means the check expects `FREE1`; at the other four it expects `FREE1@WAY`.

## STANDING RULE — login user is ALWAYS the FREE1 service account

**Never attempt to log into Bravo as PMoney, Preston Peters, Walker Tapley, or any other named user.** The watcher's service account is `FREE1@WAY` at CUL/HAR/LEX/ROA and `FREE1` (no suffix) at WAY — see the per-store override rule above. The password is stored in the watcher config (or hard-coded in `BravoAutoLogin.ahk`). Even if Bravo's Login form is pre-filled with a different username (e.g. when the Resume Session path lands on a session that was last touched by PMoney), the watcher MUST replace the User Name field with the correct per-store FREE1 form before submitting. Submitting `FREE1`'s password against any other username fails authentication, which cascades into `RecoverFromAutoLock: timeout waiting for Dashboard` and wedges every subsequent cell.

This rule is enforced in `lib/StoreCycle.ahk` Step 5: the login block always overwrites the User Name field via `^a`+`{Delete}`+paste, regardless of which branch we came from (End Session, Resume Session, or New User). Defensive logging records the pre-fill value when it differs from `FREE1@WAY` so the next assistant can spot near-misses.

If a future patch ever needs to log in as a different user, it must go through Joshua first.

## Step 1 — Diagnose

```bash
# Last log line
tail -5 '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/logs/<trigger-id>.log'

# Last log mtime
stat -f '%Sm' '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/logs/<trigger-id>.log'

# Wall clock
date

# Files produced so far
find '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/' -newer '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/triggers/<id>.json' -type f
```

Capture the last log line — it tells you where in `SwitchStore` / `Lock Session` / `Submit` / etc. the hang occurred. Save this for the DM and for updating the hang-patterns section below.

## Step 2 — Find and kill the watcher PID

```bash
/usr/local/bin/prlctl exec '{7dc84f03-4e68-4f43-9596-bf8a7dfb8e0a}' --current-user wmic process where 'name="AutoHotkey64.exe"' get ProcessId,CommandLine
```

You will see two AHK processes typically:
- `BravoAutoLogin.ahk` — the tray helper that keeps Bravo logged in. **Leave it alone.**
- `bravo_watcher.ahk` — the watcher. **This is the one to kill.**

Kill ONLY the watcher PID:

```bash
/usr/local/bin/prlctl exec '{7dc84f03-4e68-4f43-9596-bf8a7dfb8e0a}' --current-user taskkill /F /PID <pid>
```

Verify it's gone:

```bash
/usr/local/bin/prlctl exec '{7dc84f03-4e68-4f43-9596-bf8a7dfb8e0a}' --current-user tasklist /FI 'IMAGENAME eq AutoHotkey64.exe'
```

Should show only `BravoAutoLogin.ahk`'s PID.

## Step 3 — Move the stuck trigger out of the queue

If you leave the trigger file in `triggers/`, the restarted watcher will immediately pick it back up and re-hang on the same cell.

```bash
mv '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/triggers/<id>.json' \
   '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/triggers/processed/<id>.json'
```

## Step 4 — Restart the watcher

```bash
/usr/local/bin/prlctl exec '{7dc84f03-4e68-4f43-9596-bf8a7dfb8e0a}' --current-user 'Y:\Documents\Claude\Projects\Bravo Data Extraction\start_watcher.bat'
```

The script's exit code may be 2 (CMD quirk with `start`) — that's fine. Verify success by:

- A new AHK PID appears in `tasklist`
- `logs/watcher.last_started.txt` has a fresh timestamp

## Step 5 — Determine what completed

Compare the original trigger's `reports` array against CSVs in `output/` that are newer than the trigger drop time. Anything missing needs to be re-pulled.

The trigger processes reports in array order, and within each report processes stores in array order (CUL → HAR → LEX → ROA → WAY). The hang point in the log tells you the exact cell that wedged — everything before that cell completed.

## Step 6 — Drop a follow-up trigger

New trigger ID like `<original-name>-followup-YYYY-MM-DDTHH-MM-SS`. Include ONLY the missing (report, store) pairs. Example for a hang at LEX layaway:

```json
{
  "id": "monday-bravo-followup-2026-05-13T08-22-00",
  "requested_at": "2026-05-13T08:22:00-04:00",
  "reports": [
    {"name": "layaways", "stores": ["LEX","ROA","WAY"], "date": "2026-05-12"},
    {"name": "employee-activity", "stores": ["CUL","HAR","LEX","ROA","WAY"], "date": "2026-05-01"},
    {"name": "chekkit-inactives", "stores": ["CUL","HAR","LEX","ROA","WAY"], "date": "2026-05-12"}
  ]
}
```

## Step 7 — Poll the follow-up, then run chained SKILLs

Poll the same way as the original. When complete, run the chained SKILL parse+post phases for the reports that were missing.

## Step 8 — DM Joshua

After recovery, DM Joshua (`U03BB52MDSA`) with a brief recovery summary:

```
Watcher hang auto-recovered.

Hang point: <last log line>
Hung for: ~N minutes before recovery started
Killed PID: <pid>
Restarted watcher: <timestamp>
Follow-up trigger: <id>

Reports recovered automatically: <list>
Reports still pending follow-up completion: <list>

If this hang pattern is new (not in recovery.md), I've appended it to the
hang-patterns section.
```

## If recovery itself fails

Stop. Do not loop. DM Joshua with all diagnostic data captured so far and let him intervene manually:

- Original trigger ID and contents
- Last log line and timestamp
- Whether `taskkill` succeeded
- Whether the watcher restarted (new PID present? `last_started.txt` updated?)
- Whether the follow-up also hung

## Hang patterns observed (append new ones here)

### 2026-05-12 — Resume Session post-Submit UIA hang

**Symptom:** `SwitchStore` for LEX (and possibly other stores after the first cycle) took the "Resume Session" branch on the Session List screen, clicked Submit, then the post-Submit `GetCurrentStoreCode` UIA call blocked indefinitely. The 25s timeout inside the wait loop never fired because the UIA call itself never returned. Last log line: `SwitchStore: click Submit`.

**Root cause:** Bravo's session-resume flow leaves the window in a transitional UIA state that doesn't return a queryable element. The store-switch was technically successful from Bravo's perspective but the watcher could not confirm it.

**Patch applied 2026-05-13:** `lib/StoreCycle.ahk` updated to prefer **End Session** over Resume Session on the Session List screen. End Session kills the stale session and drops the watcher on a clean Login form, avoiding the brittle resume-session path. Fallback ladder: End Session → Resume Session → New User. Backup of pre-patch file: `lib/StoreCycle.ahk.bak-2026-05-12`.

**If this same hang recurs after the patch:** the End Session path may have its own UIA brittleness. Investigate by capturing screenshots inside the VM and reviewing what UI state the watcher is sitting in at the hang point. Consider adding a per-cell hard timeout in `bravo_watcher.ahk:ProcessTrigger` so a single wedged cell doesn't wedge the whole run.

### 2026-05-13 — Wrong-username cascade (chekkit phase)

**Symptom:** Follow-up trigger after the Resume Session hang produced 5/5 `EnsureStore failed` errors for chekkit-inactives (and the LEX/ROA/WAY employee-activity retries). Log pattern repeated for every store: `EnsureStore: login screen visible — recovering before evaluating store` → `RecoverFromAutoLock: login screen detected, submitting password` → `[UIA] click Submit` → `RecoverFromAutoLock: timeout waiting for Dashboard` → `EnsureStore: auto-lock recovery failed`.

**Root cause:** the Resume Session path in `SwitchStore` trusted Bravo's pre-fill of the User Name field. For sessions that had previously been used by PMoney (Preston Peters), the form was pre-filled with `PMoney` instead of `FREE1@WAY`. Submitting `FREE1`'s password against `PMoney` fails authentication, Bravo stays on the Login screen, and the auto-lock recovery loop can't dismiss it.

**Patch applied 2026-05-13:** `lib/StoreCycle.ahk` Step 5 rewritten to always overwrite the User Name field with `FREE1@WAY`, regardless of which branch reached the Login form. Added defensive `NOTE: User Name was pre-filled with '<X>'` logging when the pre-fill differs from the target — easy to grep for in logs and a signal that the previous session was started by a non-service user.

**If this same hang recurs after the patch:** check the log for the `NOTE: User Name was pre-filled` line. If present, the patch fired correctly and the issue is elsewhere (Bravo modal, password change, network). If absent, the patch may not have loaded — verify the watcher was restarted after the patch was applied (`logs/watcher.last_started.txt` timestamp).

### 2026-05-13 — Lockout incident — DO NOT REPEAT THIS PATCH

**What happened:** to address the wrong-username problem above, I patched `StoreCycle.ahk` Step 5 and `Bravo.ahk:RecoverFromAutoLock` to *always* overwrite the User Name field with `FREE1@WAY`, regardless of which branch reached the Login form. The patch used `unameElem.Focus()` wrapped in `try` followed by `Send("^a")` + `Send("{Delete}")` + paste. When `Focus()` failed silently (which it apparently can on Bravo's WPF form during transitions), `^a` + `Delete` + paste of `FREE1@WAY` landed in *whatever field Bravo currently had focused* — which was the Password field. The watcher then submitted `FREE1@WAY` as the password against whatever username was already there, repeatedly across stores, and Bravo's lockout policy triggered.

**Impact:** the `FREE1@WAY` account was locked out from Bravo. Manual reset required.

**Both patches reverted to backups:** `lib/StoreCycle.ahk.bak-2026-05-12`, `lib/Bravo.ahk.bak-2026-05-13`.

**Subsequent re-apply (2026-05-13 after the lockout):** ONLY the End Session preference patch was re-applied to `lib/StoreCycle.ahk`. The broken username-overwrite logic was NOT re-applied. The current `lib/StoreCycle.ahk` therefore has the End Session preference (Step 4 post-row Session List handler) but the original Step 5 login behavior — User Name is filled explicitly only on the New User branch, and on Resume Session / End Session branches the form's pre-fill is left alone. Pre-patch backup at `lib/StoreCycle.ahk.bak-pre-endsession-reapply-2026-05-13`. `lib/Bravo.ahk` remains at the original unmodified state.

**Lesson:** never issue keystrokes (Send/Ctrl+V) after a Focus() call without first verifying focus actually moved. UIA Focus() failures are common during WPF form transitions and they fail silently inside try/catch. If a future patch wants to overwrite the User Name field, it must:
1. Use a `Value := "..."` assignment via the UIA ValuePattern instead of keystrokes, or
2. Click the User Name field with `ClickByName` (which has its own retry/wait) and then verify the focused element's AutomationId/ControlType matches before any keystroke, or
3. Use Tab-from-anchor navigation like `BravoAutoLogin.ahk` does (Tab past everything to reset focus, then Shift+Tab back to a known field).

Any approach must be dry-run-tested against a dummy form, NOT live Bravo, before going anywhere near real credentials. And there must be a per-cell hard timeout AND an auth-failure circuit breaker armed before the patch is deployed — both of which are now in place (see "Watcher safety rails" near the top of this doc). With the breaker armed at N=3, the worst case for a future bad credential patch is 3 failed login attempts, not 13+.
