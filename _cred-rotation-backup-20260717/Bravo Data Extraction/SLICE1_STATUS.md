# Slice 1 — Status & how to test it

_Updated 2026-05-12._

## What's done

Everything except the live end-to-end test. All code lives at `~/Documents/Claude/Projects/Bravo Data Extraction/` (Mac side) = `Y:\Documents\Claude\Projects\Bravo Data Extraction\` (VM side).

| Piece | Status |
|---|---|
| Folder structure (`lib/`, `reports/`, `triggers/`, `output/`, `results/`, `logs/`) | Done |
| `config.json` with your real credentials | Done (not committed; in `.gitignore`) |
| `config.example.json` template | Done |
| `lib/Bravo.ahk` (Bravo wrapper functions) | Done |
| `lib/Json.ahk` (JSON I/O via PowerShell) | Done |
| `reports/SafeRegisterJournal.ahk` — **with real Bravo navigation** | Done |
| `bravo_watcher.ahk` (persistent poller) | Done |
| `bravo_export.ahk` (one-shot manual runner) | Done |
| `README.md` (usage + setup) | Done |
| Windows Startup shortcut for `bravo_watcher.ahk` | Done — at `C:\Users\joshuadavis\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\BravoWatcher.lnk` |
| End-to-end smoke test against a live Bravo session | **TODO — needs you to watch** |

## What I learned about Bravo's UI (verified, not guessed)

The Safe Register Journal flow is:

1. Dashboard → click **Reports** in right sidebar (bottom of the list)
2. Reports listing opens; columns: Closing / Inventory / Loan / Sales reports
3. Click **Safe Register Journal** (in Closing Reports column)
4. Right panel shows Preview / Print / Done — click **Preview**
5. Modal "Safe Register Journal Report Configuration" appears with a single **Business Date** field (defaults to today)
6. Click **Ok**
7. DevExpress Report Preview opens — columns: Txn Num, Date & Time, Txn Type, Till Number, Associate, Comments, Tender Type, Amt Coll
8. Click **Export...** in toolbar
9. Export Document dialog: format dropdown (Pdf default, but **Csv is available**), file path (defaults to `\\Mac\Home\Desktop\...`), "Open file after exporting" checkbox
10. Set format = Csv, set path to our output folder, uncheck "Open file after exporting", click **OK**
11. Click **Done** twice to return to Dashboard

**Bravo can write CSV directly to our shared output folder** via the UNC path — no copy step needed. We confirmed this by exporting once manually; the CSV is at `output/2026-05-12_HAR_safe-register-journal.csv`. (DevExpress preserves visual layout, so the CSV has decoration rows, but the data is there.)

## How to run the smoke test

You start the test, I watch it. The test is non-destructive — it drives Bravo through the same clicks you'd do manually.

### Setup (do once)

1. **Put Bravo at the HAR Dashboard.** No popups, no in-progress workflows. The Bravo title bar should read `Bravo  2026.2.2.3  VALLEY PAWN - HARRISONBURG (HAR)`.

2. **Dismiss any popup** like "Till must be opened to complete a transaction" by clicking Ok.

### Run the test

Press `Win+R`, paste this exact line, press Enter:

```
"C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe" "Y:\Documents\Claude\Projects\Bravo Data Extraction\bravo_export.ahk" safe-register-journal HAR 2026-05-12
```

What you should see, in order:
- Bravo's right sidebar "Reports" gets clicked
- Reports listing screen appears, "Safe Register Journal" gets clicked, then "Preview"
- Config dialog appears; the date field gets set to `5/12/2026`; "Ok" gets clicked
- Report Preview renders
- "Export..." gets clicked
- Export dialog: format gets set to Csv, file path gets replaced with `Y:\Documents\Claude\Projects\Bravo Data Extraction\output\2026-05-12_HAR_safe-register-journal.csv`, "Open file after exporting" gets unchecked, OK gets clicked
- Done gets clicked twice to return to Dashboard
- A success message box appears with row count

**If anything goes wrong**, hit `Ctrl+Alt+Q` to kill the AHK script. Bravo will be left wherever the script was at the time; you can use Cancel / Done to navigate back to the Dashboard manually.

### Verify success

When the success dialog appears, check:

- File exists: `~/Documents/Claude/Projects/Bravo Data Extraction/output/2026-05-12_HAR_safe-register-journal.csv`
- Result JSON exists in `results/` with `"status": "success"`
- Log file in `logs/` shows the sequence of clicks with no errors

### What's brittle in slice 1

The script clicks by **pixel coordinate**, not by UI element name. That works at the current Bravo window size but breaks if:
- You resize the Bravo window
- Bravo updates and shifts a button by a few pixels
- Windows DPI scaling changes

Slice 2 replaces the coordinate clicks with the UIA-v2 library (community AHK library for proper UI element addressing) which is robust to all of those. For slice 1 we accept the brittleness in exchange for getting the pipeline proven end-to-end faster.

## After slice 1 passes — what comes next

1. **Slice 2: store cycling.** Port the `bravo-store-cycle` Lock Session → Global Access → pick store → login flow into AHK. Then the script can pull SRJ for all 5 stores from a single trigger.
2. **Slice 2: UIA-v2.** Vendor the library and replace coordinate clicks with element lookups.
3. **Slice 3+: more reports.** Loans 75-day past due, Layaways, Aged Inventory, Employee Activity, Company KPIs, Sales-by-Vendor, Chekkit Inactives, Till Register Journal.
4. **Slice 4: re-point scheduled tasks.** Daily Funds Verification → Loan/Layaway → Monday Combined Run → New Inv Weekly Report all start using trigger files instead of computer-use.

## What I will not do without further approval

- Modify your existing `BravoAutoLogin.ahk` — I haven't touched it; it's still your tool.
- Auto-launch the watcher on a live store run until slice 1 is signed off.
- Re-point any scheduled task off computer-use until the underlying report module has been validated.
