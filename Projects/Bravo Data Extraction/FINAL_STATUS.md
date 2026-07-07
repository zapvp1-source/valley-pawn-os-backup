# Final Status - End of 2026-05-12 Session 2

## Headline

**5/5 SRJ extraction across all Valley Pawn stores, end-to-end via single trigger file. Zero Mac computer-use clicks.** Run `srj-all-stores-7` produced real CSVs for CUL (28 rows), HAR (27), LEX (33), ROA (29), WAY (31) in 4.5 minutes total. Daily Funds Verification scheduled task can now be re-pointed at this pipeline.

## What works end-to-end

The complete Mac->VM SRJ pipeline:

1. Mac drops a trigger JSON into `triggers/<id>.json`
2. AHK watcher (`bravo_watcher.ahk`) running inside Parallels Windows VM polls the folder every 30s
3. For each requested (store, date) cell:
   - SwitchStore drives Bravo's Lock Session -> Session List (End Session OR Resume Session) -> Login form -> password -> landed
   - SafeRegisterJournal opens Reports -> double-clicks tile -> sets Business Date -> Preview renders -> Export Document dialog -> sets Csv format via combobox click+select -> sets file path via inner Edit ValuePattern -> unchecks open-after-export -> clicks OK
   - CSV lands in `output/YYYY-MM-DD_STORE_safe-register-journal.csv`
4. Result JSON in `results/<id>.result.json` reports per-cell status
5. Mac reads the CSVs and result JSON; never touches Bravo

## Files in working state

```
Bravo Data Extraction/
  lib/Bravo.ahk                       UIA helpers, BackToDashboard (waits for Reports, no Esc),
                                      DismissPopups (btnOk + Remind Me Later),
                                      RecoverFromAutoLock (Session List -> Resume Session)
  lib/StoreCycle.ahk                  Lock Session -> Session List (End Session OR Resume Session)
                                      -> Global Access OR direct -> Login form -> password -> landed.
                                      Defensive try/catch around UIA polling.
  lib/UIA-v2/UIA.ahk                  vendored Descolada UIA-v2
  lib/Json.ahk                        pure-AHK JSON I/O
  reports/SafeRegisterJournal.ahk     full SRJ flow + Export Document dialog
                                      (combobox expand+select, child Edit ValuePattern,
                                       CheckBox sweep for Open file after exporting)
  reports/UIADiscover.ahk             tree dumper
  bravo_watcher.ahk                   persistent poller, #SingleInstance Force
  bravo_export.ahk                    manual one-shot runner
  config.json                         credentials

  output/2026-05-12_CUL_safe-register-journal.csv  28 rows, real data
  output/2026-05-12_HAR_safe-register-journal.csv  27 rows, real data
  output/2026-05-12_LEX_safe-register-journal.csv  33 rows, real data
  output/2026-05-12_ROA_safe-register-journal.csv  29 rows, real data
  output/2026-05-12_WAY_safe-register-journal.csv  31 rows, real data
```

## Big lessons learned this session (don't relearn)

1. **DevExpress Export Document combobox** does not respond to ExpandCollapsePattern (throws "Invalid IUnknown interface pointer"). The reliable path is physical `combo.Click("left")` to expand, then `ClickByName("Csv")` on the popup item.

2. **Bravo's Session List screen** appears with three states:
   - After Lock Session (between Lock and Login form) -> click "End Session" to log out
   - After double-clicking a store row (existing session for that store) -> click "Resume Session" (NOT New User; Bravo will reject New User with "You are already logged in" modal)
   - As starting state when watcher boots -> RecoverFromAutoLock handles via Resume Session

3. **Title bar shows store code even on the Login screen.** `GetCurrentStoreCode()` alone is not sufficient to confirm "landed" - must also confirm `!IsOnLoginScreen()`.

4. **WPF password field Focus() is unreliable.** After filling User Name, `Send("{Tab}")` to move focus to the Password field is more reliable than `pwElem.Focus()` because the password input element often doesn't expose a focusable UIA element.

5. **In-app popups need both AutoId-based and Name-based handling.** `btnOk` AutoId covers "Till must be opened" / "Invalid login" / "You are already logged in" / generic Info dialogs. The Overdue Task Reminder uses a `Remind Me Later` button instead - we click that by Name.

6. **Esc is dangerous post-login.** BackToDashboard used to fall back to `Send("{Esc}")` when no btnDone visible. On a freshly-rendered Dashboard, Esc can drop Bravo back to the Session List, breaking subsequent runs. Now we wait for Reports to appear instead.

7. **UIA calls can throw 0x80131505** (ArgumentException) during transition moments when Bravo's window briefly disappears or re-renders. SwitchStore's post-Submit wait loop now wraps `GetCurrentStoreCode()` and `IsOnLoginScreen()` in try/catch and skips bad iterations rather than crashing the whole run.

8. **File Explorer with project folder open breaks watcher startup.** WinExist("Bravo ") matches the Explorer window titled "Bravo Data Extraction" first. Always close File Explorer before running.

9. **Watcher restart**: double-click `bravo_watcher.ahk` from File Explorer; `#SingleInstance Force` handles replacement. AHK tray Reload Script is unreliable to target from Mac side (Mac apps grab focus through Parallels).

## Next steps (the slice 4 mechanical phase)

Slice 3 (UIA framework + SRJ proven end-to-end) is fully done. Slice 4 is now mechanical work:

1. **Re-point Daily Funds Verification scheduled task** to drop a `safe-register-journal` trigger instead of using computer-use. ~30 minutes. The first deliverable that runs without Mac driving Bravo's UI.

2. **Build remaining 8 reports** by copying `reports/SafeRegisterJournal.ahk`, renaming, updating the nav clicks. Each is 20-30 minutes once the framework is proven (it is). Priority order:
   - Loans 75-Day Past Due
   - Layaways
   - Aged Jewelry Markdown
   - Aged General Merch Markdown
   - Employee Activity
   - Till Register Journal
   - Chekkit Inactives
   - Sales by Vendor

3. **Company KPIs** is a special case (SSRS browser, not native UI). Likely a direct HTTPS GET to the SSRS URL with `&rs:Format=CSV`. Separate code path.

4. **Re-point remaining scheduled tasks** as their underlying reports come online:
   - Weekly Loan & Layaway Review
   - Monday Combined Run
   - New Inv Weekly Report
   - Chekkit Tuesday Review Requests

Total runway to "all scheduled tasks off computer-use": ~4-5 focused hours.

## Pickup sequence for next session

1. Verify VM state - Bravo should be on WAY Dashboard or close. If on Session List or Login: drop any SRJ trigger; the watcher's RecoverFromAutoLock handles cleanup.
2. Confirm watcher is running (taskbar AHK icon).
3. Start with Daily Funds Verification re-point (highest ROI - immediate user-facing win).
