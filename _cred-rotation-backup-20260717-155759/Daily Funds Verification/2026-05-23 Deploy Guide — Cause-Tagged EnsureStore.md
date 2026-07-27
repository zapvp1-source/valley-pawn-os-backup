# Deploy Guide — Cause-Tagged EnsureStore Fix

**What this guide is for:** I've already applied three patches to the Bravo Data Extraction watcher on your Mac filesystem. They're live in:

- `lib/StoreCycle.ahk`
- `lib/Bravo.ahk`
- `bravo_watcher.ahk`

Backups (with `.bak-pre-cause-tagged-2026-05-24` suffix) sit next to each original. The watcher hasn't picked up the changes yet — it's still running the old `claim-fix-2026-05-13` build it loaded at 15:31 today. Per your standing rule, `lib/*.ahk` edits are dead until `restart_watcher.bat` runs on the Windows VM.

## What the patches actually do

1. **Cause-tagged EnsureStore failures.** A new global `ENSURESTORE_LAST_CAUSE` is set at every failure path in `EnsureStore` / `SwitchStore` with one of: `login`, `nav`, `ready`, `session`, `store-row`. The watcher's auth-failure circuit breaker now ticks **only** on `cause = login`. Today's failure (`nav`) would no longer trip the breaker — ROA and WAY would still get attempted.

2. **Screenshot on failure.** A new `ScreenshotToFile(tag)` helper takes a PNG of the full screen and saves it to `logs/<triggerId>_<tag>.png`. Called from every EnsureStore/SwitchStore failure path AND from the new BackToDashboard fallback. Next time the watcher fails, we get a picture.

3. **Esc fallback in BackToDashboard.** After the 6 hops of "waiting for Dashboard to render" exhaust without finding the Reports tree, the watcher now sends Esc × 3 and re-checks for Reports. If that drops it to Session List or Login, the next `EnsureStore` call detects it via `IsOnLoginScreen()` and `RecoverFromAutoLock` logs back in.

## Steps to deploy and re-verify today

### 1. Get Bravo back to a known state (Windows VM)

1. Open Parallels → focus the Windows VM.
2. Look at what Bravo is showing. Likely options:
   - An expired-session prompt → click Resume Session (or whatever brings the login form up), log back in as FREE1@WAY.
   - A modal dialog the watcher didn't know about → take note of the title (helpful diagnostic), click whichever button gets you out.
   - A stuck report preview → click Done.
3. Confirm you're on the Dashboard — the Reports tree should be visible on the left sidebar.

### 2. Restart the watcher (Windows VM)

Double-click `restart_watcher.bat`. Watch the console window — you should see the watcher banner come up and a new line appended to `logs/watcher.last_started.txt`. The build tag is still `claim-fix-2026-05-13` (we didn't change that constant), but the new code paths will run.

### 3. Re-trigger today's verification (Mac, via me)

Once you confirm steps 1 and 2 are done, tell me "re-run today's funds verification" and I'll drop a fresh trigger with `date = 2026-05-23`. Expected behavior:

- All 5 cells should reach `EnsureStore` successfully and run.
- If any cell fails, the log will now say which cause (e.g. `cause=nav`), and a PNG will be in `logs/`.
- The circuit breaker should NOT trip unless we actually hit 3 real login failures.

### 4. Quick sanity tests (optional but cheap)

If you want to actively verify the breaker still protects you, the easy test is to leave config.json alone (don't risk wrong-password attempts on real Bravo). Instead, the next time any non-funds Bravo job runs and a single store fails with `nav`, check `logs/<triggerId>.log` for:

- `EnsureStore failure cause=nav — NOT a lockout risk; breaker not incremented`

That single log line confirms the discriminator is working.

## Rollback

If anything looks worse than it is now, restore the backups:

```cmd
cd Y:\Documents\Claude\Projects\Bravo Data Extraction
copy /Y lib\StoreCycle.ahk.bak-pre-cause-tagged-2026-05-24 lib\StoreCycle.ahk
copy /Y lib\Bravo.ahk.bak-pre-cause-tagged-2026-05-24 lib\Bravo.ahk
copy /Y bravo_watcher.ahk.bak-pre-cause-tagged-2026-05-24 bravo_watcher.ahk
restart_watcher.bat
```

That puts you back to the build tag `claim-fix-2026-05-13` you were on before.

## What's NOT in this round

I deliberately did NOT add Fix 3 (kill-and-relaunch Bravo on persistent nav failure) from the original plan. That fix is more invasive and could surprise you. With the first three fixes in place, a wedged Bravo will at least produce a screenshot showing what wedged it. Once we see a few of those, we'll know whether kill-and-relaunch is worth adding or whether a more targeted recovery action (e.g. another UIA element to look for in `BackToDashboard`'s hop loop) would be cheaper.
