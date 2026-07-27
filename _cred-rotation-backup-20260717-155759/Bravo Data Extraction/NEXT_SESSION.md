# Next Session — Pickup Notes

_Written 2026-05-12 12:21 PM at the end of a long session._

## The 10-minute pickup script for next session

1. **Recover Bravo state.** Bravo VM ended this session on "Open Till" screen. Click Cancel manually (or via the watcher cycling) to get back to Dashboard.

2. **Launch the watcher.** `Win+R`, paste:
   ```
   "C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe" "Y:\Documents\Claude\Projects\Bravo Data Extraction\bravo_watcher.ahk"
   ```
   You should see the tray notification "Bravo Watcher started".

3. **Drop a single-store SRJ test trigger.** Write a `triggers/srj-cul-test.json`:
   ```json
   {
     "id": "srj-cul-test",
     "requested_at": "2026-05-12T...",
     "reports": [{"name": "safe-register-journal", "stores": ["CUL"], "date": "2026-05-12"}]
   }
   ```

4. **Read the result + log.** If success: rejoice. If error: the diagnostic dump in the log tells you exactly which UIA element name needs adjusting in `reports/SafeRegisterJournal.ahk`.

## What's DEFINITELY working as of end-of-session

- UIA-v2 library vendored and loading (no import errors)
- UIA helper toolkit in lib/Bravo.ahk (verified by successful clicks on Reports, Safe Register Journal, Preview-via-double-click, Business Date paste, Ok button, Export menu item)
- In-app modal popup dismissal via `btnOk` AutoId — proved by `[popup] dismissed via btnOk` log entry
- Store cycling primitive (proved end-to-end in slice 2)
- Pipeline plumbing (trigger → watcher → handler → result JSON + log)

## What needs to land in the next session

1. **BackToDashboard hardening.** It uses `Dashboard.Buttons.Reports` AutoId now (was using ambiguous "Reports" Name before). Should work — verify on the first test run. If it still can't recover, add an `Esc` key press to the fallback chain.

2. **Verify the Export Document dialog name fixes already in code.**
   - `Export format` (lowercase f)
   - `File path` (lowercase p)
   - `Open file after exporting` (no leading "the")
   - These three are landed in `SRJ_ELEMENTS` but haven't been verified end-to-end yet. The previous tests got blocked before reaching these steps.

3. **Multi-store SRJ test** — drop a trigger with `"stores": ["CUL","HAR","LEX","ROA","WAY"]`. Runtime ~3 minutes. 5 CSVs should land.

After those three are green, slice 3 is fully done.

## File state at end of session

All slice-3 files in their refactored UIA form:
- `lib/Bravo.ahk` — UIA helpers + BackToDashboard(AutoId-based) + DismissPopups(btnOk-aware)
- `lib/StoreCycle.ahk` — UIA-based
- `reports/SafeRegisterJournal.ahk` — UIA-based, calls BackToDashboard at start, DismissPopups between steps
- `reports/UIADiscover.ahk` — tree-dump helper
- `lib/UIA-v2/UIA.ahk` — vendored library

## Important reminders from today

- **AHK source must be ASCII.** Em-dashes and smart quotes in comments break the parser. Stick to `-` and `"`.
- **`elem.Click("left")` not `elem.Click()`** for WPF tree-view items (Reports sidebar etc.).
- **AutomationId beats Name** when available. Bravo's Dashboard sidebar exposes stable IDs like `Dashboard.Buttons.Reports`, `btnDone`, `btnOk`. Prefer them.
- **Bravo's in-app modals** (like "Till must be opened") are not Windows-level popups — they're WPF overlays with a `btnOk` button. `DismissPopups` now handles this via UIA.
- **`type` drops characters on the slow VM.** Always use clipboard + Ctrl+V.

## After slice 3 is fully green

Slice 4: build the remaining 8 reports (~20-30 min each). Order by impact: Loans 75-Day, Layaways, Aged Jewelry Markdown, Aged GM Markdown, Employee Activity, Till Register Journal, Chekkit Inactives, Sales by Vendor. Company KPIs special-cased via direct SSRS HTTPS.

Slice 5: re-point scheduled tasks to use trigger files (Daily Funds Verification, Weekly Loan & Layaway Review, Monday Combined Run, New Inv Weekly Report, Chekkit Tuesday).

Total runway from here to "all scheduled tasks off computer-use": ~5-6 focused hours.
