# Funds Verification — Fix Plan to Stop Partial Days

**Why we keep getting partial / failed days:** The watcher's auth-failure circuit breaker is too aggressive. It trips on *any* string containing "EnsureStore failed" — but most of the recent failures aren't auth failures at all, they're navigation failures (Bravo is stuck off-Dashboard, so `BackToDashboard` times out, so `Lock Session` can't be clicked, so EnsureStore reports a generic failure). The breaker meant for password-lockout protection is killing healthy runs.

## What actually happened the last 4 days

| Date | Result | Real cause |
|---|---|---|
| 2026-05-20 | 5/5 ✓ | Clean run — Bravo on Dashboard, watcher happy |
| 2026-05-21 | 4/5 — ROA failed | ROA-specific store-cycle issue (the known "canary" failure) |
| 2026-05-22 | 0/5 — "Bravo window not found/ready within 30s" all 5 | Bravo wasn't running on the VM (crashed or closed) |
| 2026-05-23 | 0/5 — 3× EnsureStore failed → circuit breaker tripped | Bravo IS running but stuck off-Dashboard; `BackToDashboard` can't recover |

The May-23 watcher log shows the exact failure on every store:

```
SwitchStore: BackToDashboard before Lock Session
  [nav] BackToDashboard: waiting for Dashboard to render  (×6)
SwitchStore: WARNING — could not reach Dashboard; trying Lock Session anyway
SwitchStore: click Lock Session
SwitchStore: Lock Session click failed: ClickByName: element not found: Lock Session
ERROR: EnsureStore failed for CUL
  consecutiveAuthFailures = 1/3
```

None of the recovery actions inside `BackToDashboard` (modal Cancel, btnCancel, Cancel-by-name, btnDone) matched anything on screen — so whatever screen Bravo is sitting on isn't one of the known states. Without a screenshot we can't tell exactly what it is, but it's almost certainly one of: an expired-session login prompt, a "Bravo updating" splash, or an unexpected dialog the watcher doesn't know about.

## Tonight — manual recovery (15 min)

This is the only path to verify today's $8,000 because the CSVs don't exist yet.

1. Open the Parallels Windows VM.
2. Look at what Bravo is currently showing. Most likely you'll see one of: a login screen, an "Are you still there?" prompt, or some report preview that nobody dismissed.
3. Click whatever it takes to get back to the Dashboard (Reports tree visible in the left sidebar).
4. Double-click `restart_watcher.bat`.
5. Then back on this Mac, ask me to "re-run today's funds verification" — I'll drop a new trigger with today's date and finish the reconciliation.

## Durable fixes — the AHK changes to stop this recurring

I'm not auto-editing your `.ahk` files because **per your standing rule, any `lib/*.ahk` edit is dead until the watcher restarts** (and we just talked about not making more bad logins). But here are the four changes I'd like to make and the reasons:

### Fix 1 — Make the circuit breaker distinguish nav from auth (highest leverage)

`bravo_watcher.ahk` line 322 currently does:

```ahk
if (cellStatus = "error" && InStr(cellError, "EnsureStore failed")) {
    consecutiveAuthFailures += 1
    ...
}
```

This treats every EnsureStore failure as a possible password lockout, including pure nav failures. Change to match only on a more specific signal that the report handlers produce when `IsOnLoginScreen()` was true and `BravoLogin` actually failed — for example, `"EnsureStore failed (login)"`. Make the report-handler error string carry the cause:

```ahk
; in StoreCycle.ahk EnsureStore / SwitchStore
return false, "nav"   ; when BackToDashboard or Lock Session click fail
return false, "login" ; when RecoverFromAutoLock returned false
return false, "ready" ; when WaitForBravoReady timed out
```

And the report handlers thread the cause into the cell's `error` field. Then the watcher only ticks the lockout counter on `(login)`.

**Effect**: today's failure mode (nav-stuck) would have produced 5 errors but no breaker trip, and ROA/WAY would still have been attempted. The breaker stays in place for the actual risk (wrong-password cascade).

### Fix 2 — Screenshot on EnsureStore failure (forensics)

Add to `StoreCycle.ahk` at every `return false` path inside `EnsureStore` / `SwitchStore`:

```ahk
ScreenshotToFile(CONFIG["paths.logs"] . "\" . TRIGGER_ID . "_" . targetStore . "_failure.png")
```

Right now we can't tell *what* Bravo was showing — we just see "waiting for Dashboard to render" six times in the log. A PNG would close the loop in seconds.

### Fix 3 — Kill-and-relaunch Bravo on persistent nav failure

If two consecutive cells fail with nav errors, the watcher should:

1. `taskkill /F /IM Bravo*.exe`
2. `Run "<Bravo launch path>"`
3. `WaitForBravoReady(60)` + `BravoLogin(password)`
4. `BackToDashboard()`
5. Retry the failed cell

This handles the "Bravo wedged off-Dashboard" case automatically. We treat it differently from auth failures so the lockout breaker still protects us.

### Fix 4 — Add Esc fallback to `BackToDashboard` post-hop-exhaustion

The current code explicitly avoids Esc because it can drop to Session List on freshly-authenticated Bravo. But if we've already exhausted 6 hops with no recovery, we're in a worse state than Session List. After hops exhaust:

```ahk
; Last-resort: send 3 Esc presses, wait, recheck
loop 3 {
    Send "{Escape}"
    Sleep 800
}
DismissPopups()
if FindByName("Reports", 4000) {
    LogMessage("    [nav] BackToDashboard: recovered via Esc fallback")
    return true
}
; If we land on the Login screen via Esc, IsOnLoginScreen will catch it
; on the next EnsureStore call and RecoverFromAutoLock will log us back in.
```

## Test plan after edits

After applying Fixes 1–4 and running `restart_watcher.bat`:

1. **Smoke test (must pass)**: Drop a trigger for safe-register-journal × all 5 stores against today's date. Expect 5/5 success.
2. **Lockout-protection test (must still trip the breaker)**: Temporarily set a wrong password in `config.json`, drop a trigger, confirm watcher trips after 3 `(login)` failures and skips remaining stores.
3. **Wedge-recovery test (must auto-recover)**: Manually leave Bravo on a report preview, drop a trigger, confirm Fix 3 kicks in after 2 nav failures and the run completes.
4. **Forensics test**: Manually break navigation (close all Bravo windows), drop a trigger, confirm a `*_failure.png` lands in `logs/`.

## What I want from Joshua

A green light on the four fixes above. Once you say go, I'll prepare the exact diffs against `lib/StoreCycle.ahk`, `lib/Bravo.ahk`, and `bravo_watcher.ahk`. You apply them on the VM, run `restart_watcher.bat`, and we run the test plan together. That's the path to "all 5 stores verified daily, no partials."
