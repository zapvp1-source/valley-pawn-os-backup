# Continuation Plan — Bravo Data Extraction

_Written end of session 2026-05-12 by the previous session._

## State of the world right now

**What works (proven end-to-end today):**
- Pipeline: trigger JSON → watcher → AHK script → CSV in output → result JSON. Zero computer-use clicks from the Mac. Slice 1 confirmed with `slice1-test-8` producing `output/2026-05-12_HAR_safe-register-journal.csv`.
- Store cycling primitive: `SwitchStore("CUL", password)` successfully drove Lock Session → Global Access → CUL row → password paste → Submit → "landed on CUL". Slice 2 core confirmed with `slice2-cycle-cul-3` (cycle log line 17).
- Mac↔VM file bridge via `Y:\Documents\Claude\Projects\Bravo Data Extraction\`.
- Auto-launch watcher on Windows login via Startup shortcut.
- Pure-AHK JSON parser (no PowerShell encoding pain).

**What doesn't work yet:**
- SRJ flow on stores other than HAR sometimes hits banner ads and opens Chrome mid-run. Root cause: coordinate-based clicks are fragile to banner rotation and per-store layout drift.
- No reports built beyond Safe Register Journal.

**Open items at the end of this session:**
- Bravo VM is currently on the CUL Session List screen (Resume Session / End Session / New User visible). Joshua can recover by clicking Resume Session or End Session before any new run.

## The plan — execute in this exact order

### Step 1 — Vendor UIA-v2 library (Descolada/UIA-v2 on GitHub)

The library is the AHK community standard for Windows UI Automation. It gives us element-by-name lookups, the same way pywinauto and FlaUI do.

- Save `Lib/UIA.ahk` (the main file) into `lib/UIA-v2/UIA.ahk` in this project
- Save `Lib/UIA_Browser.ahk` if needed (probably not for Bravo)
- Source: `https://github.com/Descolada/UIA-v2` — `Lib/UIA.ahk` raw file

If WebFetch can't reach GitHub raw URLs from the sandbox, the user can clone it locally and copy. Either way it's a one-time vendor.

### Step 2 — Replace coordinate clicks in `lib/Bravo.ahk` with UIA element lookups

Pattern to follow:

```ahk
; OLD (slice 1):
Click(realX, realY)

; NEW (slice 3):
elem := bravoWin.FindElement({Name: "Lock Session"})
elem.Click()
```

Key elements that need named lookup wrappers:
- Window: `bravoWin := UIA.ElementFromHandle(WinExist("Bravo "))`
- Right sidebar Reports
- Lock Session in top-right user menu
- Global Access link on Login screen
- Switch User / Submit / Resume Session buttons
- Password field
- Store Selector rows (by store name)
- "Safe Register Journal" report tile in Reports listing
- Right-panel Preview / Done buttons
- DevExpress toolbar Export button
- Export Document dialog: format combo, file path text input, "Open file after exporting" checkbox, OK button

Add a helper in `lib/Bravo.ahk`:

```ahk
ClickByName(name, parent := "") {
    win := parent ? parent : UIA.ElementFromHandle(WinExist("Bravo "))
    elem := win.FindElement({Name: name})
    elem.Click()
    LogMessage("    click [UIA] " . name)
}
```

Then `reports/SafeRegisterJournal.ahk` becomes:

```ahk
ClickByName("Reports")
Sleep(1500)
ClickByName("Safe Register Journal")
ClickByName("Preview")
SetBusinessDate(date)
ClickByName("Ok")
...
```

Coordinate tables go away. The `COORD_SCALE_X/Y` / `Y_OFFSET` machinery goes away. Banner rotation can't hijack clicks anymore.

### Step 3 — Re-test SRJ on HAR (should still work)

Drop a trigger like:

```json
{"id":"slice3-srj-har","reports":[{"name":"safe-register-journal","stores":["HAR"],"date":"2026-05-12"}]}
```

Confirm CSV lands in `output/`.

### Step 4 — Re-test SRJ on CUL with cycling (the slice-2 failure case)

Drop a trigger with `stores: ["CUL"]`. With UIA-v2 driving clicks, the CUL run should succeed where it failed today.

### Step 5 — Multi-store SRJ trigger

Drop one trigger with `stores: ["CUL","HAR","LEX","ROA","WAY"]`. Expected runtime ~200 seconds (5 × ~40s). Five CSVs land. Result JSON shows 5 cells, status=success.

### Step 6 — Build out report modules (order by impact)

For each, copy `reports/SafeRegisterJournal.ahk`, rename function and slug, change the click sequence to match the report's nav path. Each module is ~50 lines.

1. **Loans 75-Day Past Due** (slug `loans-75-days-past-due`) — Loans/Buys sidebar → "Loans To Expire" → Custom Reports → Choose Saved Report "75 Days Past Due" → Ok → read title bar count, read summary panel sum
2. **Layaways** (slug `layaways`) — Layaways sidebar → read 5 badge counts (Layaways Overdue / Past Payment Due Date / Contacted But No Activity / No Payment in 30 days / Locate Layaways). Output format: single CSV row per store with all 5 columns.
3. **Aged Jewelry Markdown** (slug `aged-jewelry-markdown`) — Inventory sidebar → Custom Reports → "Aged Jewelry Markdown" → Ok → read Sum from summary panel
4. **Aged General Merch Markdown** (slug `aged-general-merch-markdown`) — same pattern, different saved report
5. **Employee Activity** (slug `employee-activity`) — Reports listing → Employee Activity tile → Preview → date range (first of month to today) → Ok → Export to Csv
6. **Till Register Journal** (slug `till-register-journal`) — Reports listing → Till Register Journal tile → mirrors SRJ exactly
7. **Chekkit Inactives** (slug `chekkit-inactives`) — saved report, last 7 days, export to Csv
8. **Sales by Vendor** (slug `sales-by-vendor`) — Reports module → Sales Report → date range + vendor multi-select → Export to Csv. Vendor list comes from the trigger payload.
9. **Company KPIs** (slug `company-kpis`) — special case. Dashboard → Reporting Pro → Company KPIs opens an SSRS browser tab. Easier to bypass UI entirely: scrape the SSRS URL pattern once, then fetch directly with HTTPS + `&rs:Format=CSV`. Different code path; consider a separate `lib/SSRS.ahk` module.

### Step 7 — Re-point existing scheduled tasks

Once a report is proven, update the corresponding scheduled task's skill to drop a trigger file instead of using computer-use:

| Scheduled task | Replace with trigger | Status |
|---|---|---|
| Daily Funds Verification | `safe-register-journal` × 5 stores | Ready to re-point (after slice 4 — see below) |
| Weekly Loan & Layaway Review | `loans-75-days-past-due` + `layaways` × 5 stores | After step 6.1 + 6.2 |
| Monday Combined Run | 6-report trigger | After steps 6.1–6.5 |
| New Inv Weekly Report | `sales-by-vendor` × 5 stores | After step 6.8 |
| Chekkit Tuesday Review Requests | `chekkit-inactives` × 5 stores | After step 6.7 |

### Step 8 — Handle Session List screen in `SwitchStore`

After Lock Session, Bravo sometimes shows a Session List screen first (with Resume Session / New User / End Session) instead of going straight to the Login screen. Today's slice-2 left Bravo here.

Add detection: if after Lock Session we see a button labeled "Resume Session" or "End Session", click "End Session" to fully log out, then proceed with Global Access. UIA-v2 makes this detection a one-liner.

### Step 9 — Bravo auto-lock awareness

Bravo auto-locks after some idle period. If the script runs a long sequence and gets auto-locked mid-flow, it should detect (title bar still shows store, but Login screen is visible) and re-login. Add a `RecoverFromAutoLock(password)` helper that checks for Login screen presence and submits if found.

## Hard-won lessons from today (don't relearn these)

1. **PowerShell stdout from `WScript.Shell.Exec` is UTF-16 mojibake.** Don't shell out for JSON parsing. Use AHK regex for fixed schemas, or pipe PowerShell to a temp file and `FileRead(path, "UTF-8")`.

2. **AHK v2 `CoordMode` is per-thread.** `SetTimer` callbacks run in their own thread with default `Client` mode. Call `CoordMode "Mouse", "Screen"` *inside* every handler function, not just at module load.

3. **Parallels Desktop renders the VM at internal high DPI** (4096×2168 on Joshua's Mac Studio) while screenshots from the Mac side are at the displayed window size (1456×819). Coords need scaling: `realX = capturedX × A_ScreenWidth / 1456`. Also subtract ~48px of macOS menu bar + Parallels title chrome from Y before scaling.

4. **Bravo's window title bar never changes between views.** It always reads `Bravo  2026.2.2.3  VALLEY PAWN - <STORE> (<CODE>)`. The visual page header ("Reports", "Dashboard") is in-content, not in `WinGetTitle`. So `WinWaitActive` and title-substring checks don't work for navigation detection. Use UIA element presence instead.

5. **Bravo's Dashboard has rotating banner ads** (FFL Cloud Storage, MobilePawn, etc.) with "Learn More" links that open Chrome to Bravo's marketing site. A misclick on any of those derails the script. UIA element addressing immunizes against this.

6. **The `bravo-store-cycle` skill's old coordinates** were captured under a different window state. They're close but consistently ~25-30px off. Verify before trusting any skill-documented coordinate.

7. **`Click(x, y, 2)` in AHK v2** is the double-click form. `DoubleClick` is not a thing in v2.

8. **Restart the watcher** any time you edit any `.ahk` file under this project. AHK's `#Include` is compile-time. Hotkey: `Ctrl+Alt+W` exits cleanly, then re-launch from Run dialog.

## Files cheat sheet (everything is on the Mac side)

```
~/Documents/Claude/Projects/Bravo Data Extraction/
├── bravo_watcher.ahk            persistent poller (start via Startup shortcut)
├── bravo_export.ahk             manual one-shot runner
├── config.json                  credentials + paths
├── lib/
│   ├── Bravo.ahk                Bravo wrapper (window detection, popup dismiss, logging, CSV)
│   ├── Json.ahk                 pure-AHK JSON I/O
│   ├── StoreCycle.ahk           SwitchStore / EnsureStore
│   └── UIA-v2/                  ← TODO: vendor here in slice 3
├── reports/
│   └── SafeRegisterJournal.ahk  reference module
├── triggers/                    drop JSONs here
│   └── processed/               watcher moves consumed triggers here
├── output/                      CSVs land here
├── results/                     per-trigger result JSONs
├── logs/                        per-trigger AHK logs
├── FINDINGS_AND_PLAN.md         original investigation
├── SLICE1_STATUS.md             slice 1 status
├── README.md                    usage docs
└── CONTINUATION_PLAN.md         this file
```

## What to do at the very start of the next session

1. Read this file (`CONTINUATION_PLAN.md`) and `SafeRegisterJournal.ahk` to load context.
2. Check Bravo state in the VM. Probably needs Joshua to click Resume Session or End Session to recover from where today ended.
3. Make sure the watcher is running (look for tray icon, or re-launch via Run dialog with the AHK path).
4. Execute Step 1 — vendor UIA-v2.
5. Do NOT re-discover any of the "hard-won lessons" section above.

Total estimated time to "all 10 reports working and scheduled tasks re-pointed": 12-16 hours across 3-5 sessions. Slice 3 (UIA-v2 conversion) is the longest single phase at 3-4 hours; the rest is mechanical per-report work that goes fast once UIA-v2 is in place.
