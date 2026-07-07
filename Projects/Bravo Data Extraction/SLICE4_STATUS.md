# Slice 4 — All 8 Report Modules Wired Up

_2026-05-12 — written end of build session._

## What's done

**Pipeline now supports 8 reports.** All modules wired into `bravo_watcher.ahk` and `bravo_export.ahk`. After restarting the watcher, the trigger contract accepts:

| Slug | Module | Powers SKILL | Status |
|---|---|---|---|
| `safe-register-journal` | SafeRegisterJournal.ahk | daily-funds-verification | ✅ Proven end-to-end 5/5 |
| `aged-inventory-summary` | AgedInventorySummary.ahk | weekly-aged-inventory-report | 🟡 Untested — same template as SRJ |
| `employee-activity` | EmployeeActivity.ahk | weekly-employee-sales-rankings | 🟡 Untested — date dialog may need calendar walker |
| `chekkit-inactives` | ChekkitInactives.ahk | chekkit-weekly-review-requests | 🟡 Untested — Customers sidebar path |
| `loans-75-days-past-due` | Loans75DaysPastDue.ahk | weekly-loan-layaway-review (loan side) | 🟡 Untested — reads count + $ sum |
| `layaways` | Layaways.ahk | weekly-loan-layaway-review (layaway side) | 🟡 Untested — reads 5 right-panel badges |
| `fpd-cohort` | FpdCohort.ahk | weekly-fpd-ranking | 🟡 Untested — requires saved reports to exist per-store |
| `sales-by-vendor` | SalesByVendor.ahk | new-inv-weekly-report | 🟡 Untested — date range filter |
| `company-kpis` | CompanyKpis.ahk | monday-store-rankings | ❌ Stub — needs SSRS URL captured |

## How to bring up Slice 4

### Step 1 — Restart the watcher

In the VM, close any open File Explorer window titled "Bravo Data Extraction" (it confuses `WinExist("Bravo ")`), then double-click `bravo_watcher.ahk` from a NEW File Explorer window. You should see the tray notification "Bravo Watcher started — Polling … every 30s". Check `logs/watcher.last_started.txt` — it should show the new handler list including all 9 names.

### Step 2 — Smoke-test each report

The order below knocks out the easiest ones first (SRJ template clones), then the harder reads. For each, drop a trigger like:

```json
{
  "id": "smoke-aged-inv-1",
  "requested_at": "2026-05-12T...",
  "reports": [{"name": "aged-inventory-summary", "stores": ["HAR"], "date": "2026-05-12"}]
}
```

Watch `logs/<id>.log` and `results/<id>.result.json`. If the run fails, the log's `[diag]` block lists every visible UIA element on the failing screen — read the actual element Names from the dump and update the module's `<MODULE>_ELEMENTS` Map. Iterate until success, then test multi-store with `["CUL","HAR","LEX","ROA","WAY"]`.

**Recommended test order:**

1. `aged-inventory-summary` — simplest, exact SRJ pattern with default date. ~5 min, expect success first try.
2. `employee-activity` — same pattern but uses the date dialog (Start Date). If the masked field rejects the clipboard paste, the diagnostic will show; we'll need to swap to calendar-picker walking.
3. `chekkit-inactives` — Customers → Custom Reports → saved report. The Export-from-list-view path is the risky bit; if Bravo doesn't expose Export under Layouts, the SKILL falls back to manual transcription per the original (and Phase 1 still works).
4. `loans-75-days-past-due` — count from title + $ from summary panel. The `ParseCountFromTitle` regex handles "Specific: NN" / "Loans To Expire: 0" formats.
5. `layaways` — 5 badge reads. `ReadBadgeCount` tries Text-with-trailing-number and Button-with-child-Text patterns. Diagnostic will reveal the actual UIA shape.
6. `fpd-cohort` — REQUIRES saved Ad Hoc reports named exactly "FPD Cohort Originations" and "FPD Cohort Defaults" to exist per store. The weekly-fpd-ranking SKILL says to build them on first run.
7. `sales-by-vendor` — similar to Employee Activity. Vendor multi-select is not yet implemented; first version captures all sales in the date range and downstream code filters by Bravo Item # in Procurement Log.
8. `company-kpis` — SKIP for now. See "Capturing the SSRS URL" below.

### Step 3 — Iterate from diagnostic logs

For each report that fails on first run:
1. Open `logs/<id>.log`.
2. Find the `[diag]` block dumped on failure. It lists every visible Button, Hyperlink, TreeViewItem, Text, Edit, CheckBox, ComboBox, MenuItem with their Names and AutomationIds.
3. Find the element you expected to click. Update the corresponding `<MODULE>_ELEMENTS["sidebar_X"]` entry to match the exact Name from the diagnostic.
4. The watcher reloads .ahk files only on restart. After each .ahk edit, the watcher must be restarted (Ctrl+Alt+W to exit, double-click `bravo_watcher.ahk` to relaunch).
5. Drop a fresh trigger with a new id and re-test.

Typical convergence: 2–4 iterations per report. The framework's diagnostic-on-failure pattern means every failure produces actionable info.

### Step 4 — Re-point Monday SKILLs

Once a report's pipeline cell works for all 5 stores, rewrite the corresponding `/Users/joshuadavis/Documents/Claude/Scheduled/<task>/SKILL.md` to drop a trigger instead of driving the UI. Drafts will be posted to this Bravo folder for Joshua to copy across (`/Scheduled/` isn't write-accessible from the agent session right now).

Re-point priority order:
1. `daily-funds-verification` — DRAFTED at `proposed_daily_funds_skill.md` (deploy now)
2. `weekly-aged-inventory-report`
3. `weekly-employee-sales-rankings`
4. `weekly-loan-layaway-review` (uses BOTH loans-75-days-past-due AND layaways)
5. `chekkit-weekly-review-requests` Phase 1
6. `weekly-fpd-ranking`
7. `new-inv-weekly-report`
8. `monday-bravo-combined-run` (after all five chained tasks above are pipeline-driven)
9. `monday-store-rankings` (once company-kpis is implemented)

## Capturing the SSRS URL for Company KPIs

Company KPIs renders in Edge inside the VM as an SSRS Reporting Services report. The cleanest path is a direct HTTPS GET to the report URL with `&rs:Format=CSV`, bypassing UI entirely.

Steps to capture once:
1. Inside Bravo on the VM, open Dashboard → Reporting Pro → Company KPIs → set Start Date = month-1, End Date = today → Ok.
2. When the SSRS report renders in Edge, copy the full URL from Edge's address bar.
3. Paste it as the value of `SSRS_URL_TEMPLATE` in `reports/CompanyKpis.ahk`, replacing the dates with `{START_DATE}` / `{END_DATE}` placeholders.
4. Test by visiting `<URL>&rs:Format=CSV` in Edge — should download a CSV.
5. Implement the fetch in CompanyKpis.ahk: PowerShell `Invoke-WebRequest` with the URL, write the response body to outputPath.
6. May need Edge auth cookies forwarded; if a fresh fetch returns the SSRS login page, that's the cookie problem and we'll need a one-time cookie-capture step.

This is ~30 minutes of work once the URL is captured.

## Files added/changed this session

```
reports/AgedInventorySummary.ahk    NEW
reports/EmployeeActivity.ahk        NEW
reports/ChekkitInactives.ahk        NEW  (also defines SelectSavedReport helper)
reports/Loans75DaysPastDue.ahk      NEW  (also defines ParseCountFromTitle + ReadSummaryPanelSum)
reports/Layaways.ahk                NEW  (also defines ReadBadgeCount)
reports/FpdCohort.ahk               NEW
reports/SalesByVendor.ahk           NEW
reports/CompanyKpis.ahk             NEW  (stub)
bravo_watcher.ahk                   EDITED — added 8 #Include lines + 8 handler registrations
bravo_export.ahk                    EDITED — mirrored the watcher's includes/registrations
proposed_daily_funds_skill.md       NEW (already present) — drop-in for /Scheduled/daily-funds-verification/SKILL.md
SLICE4_STATUS.md                    THIS FILE
```

## Shared helpers added inline (called by multiple modules)

- `SelectSavedReport(comboName, valueName)` — in ChekkitInactives.ahk, reused by Loans75DaysPastDue.ahk + FpdCohort.ahk
- `ParseCountFromTitle()` — in Loans75DaysPastDue.ahk, reused by FpdCohort.ahk
- `ReadSummaryPanelSum()` — in Loans75DaysPastDue.ahk, reused by FpdCohort.ahk
- `ReadBadgeCount(label)` — in Layaways.ahk, layaway-specific
- `SetReportDate(fieldName, yyyymmdd)` — in EmployeeActivity.ahk, reused by SalesByVendor.ahk

(All defined at file scope, so they're global once the module's file is `#Include`d. If a refactor consolidates these into `lib/Bravo.ahk` later, no functional change — keep it simple for now.)

## Likely failure modes per module (in order of probability)

- **All modules** — sidebar/tile click misses because the right-sidebar TreeViewItem's UIA Name doesn't match the label string. Fix: read diagnostic, update `<MODULE>_ELEMENTS["sidebar_X"]`.
- **EmployeeActivity / SalesByVendor** — masked Start Date field rejects the SetValueByName paste. Fallback: implement calendar-picker walking (open calendar, navigate to month, click day). 30-min add.
- **ChekkitInactives** — Layouts → Export menu structure may not expose CSV directly. Fallback: read list rows via UIA tree walk and write CSV ourselves (slower but bulletproof).
- **Loans75DaysPastDue / FpdCohort** — `Choose Saved Report` combobox name varies. Fallback in `SelectSavedReport`: first ComboBox by Type. Also: the keyboard down-arrow fallback isn't implemented yet; if row-click misses, throw to surface in diagnostics, then we add the keyboard walker.
- **Layaways** — Badge counts may be embedded in the right panel as nested controls rather than top-level Text. Diagnostic dump will show the actual structure.
- **FpdCohort** — Saved reports may not exist yet. First run will fail with "couldn't select FPD Cohort Originations" — that's a Bravo setup task, not an automation bug. Per the weekly-fpd-ranking SKILL, they need to be created via the criteria builder once per store.
- **CompanyKpis** — stub by design until SSRS URL captured.

## Watcher restart procedure (per FINAL_STATUS lesson #8)

1. Close any File Explorer window whose title contains "Bravo " (the project folder name matches the `WinExist` selector).
2. Open a fresh File Explorer to `Y:\Documents\Claude\Projects\Bravo Data Extraction\`.
3. Double-click `bravo_watcher.ahk`.
4. Tray notification "Bravo Watcher started" should appear.
5. Verify `logs/watcher.last_started.txt` shows all 9 handler names (uia-discover counted): `safe-register-journal, uia-discover, aged-inventory-summary, employee-activity, chekkit-inactives, loans-75-days-past-due, layaways, fpd-cohort, sales-by-vendor, company-kpis`.

After restart, drop a smoke trigger and the new modules are live.
