# Slice 3 — UIA-v2 Refactor — Status

_End of session 2026-05-12._

## Architecture: complete

- Vendored Descolada/UIA-v2 (`lib/UIA-v2/UIA.ahk`, 7946 lines, self-contained)
- `lib/Bravo.ahk` has full UIA helper toolkit: `FindByName`, `ClickByName`, `DoubleClickByName`, `ExistsByName`, `WaitForAnyByName`, `SetValueByName`, `SetToggleByName`, `GetValueByName`
- `ClickByName` uses physical mouse click (`elem.Click("left")`) — WPF tree-view items need that to fire navigation
- `lib/StoreCycle.ahk` fully refactored to UIA (Lock Session, End Session, Global Access, store row, password, Submit)
- `reports/SafeRegisterJournal.ahk` fully refactored to UIA
- `reports/UIADiscover.ahk` dumps the UIA tree to `output/uia-tree-<date>.txt` for any screen — invoke with `{"name": "uia-discover"}` trigger
- Diagnostic mode: every `ClickByName`/`SetValueByName` failure auto-dumps visible elements to the log, so each "name not found" error tells you exactly what to fix

## End-to-end verified steps (all via UIA, no coordinates)

Trigger `slice3-srj-cul-5` log shows the script driving CUL all the way through:

| Step | Result |
|---|---|
| EnsureStore (no-op when already on target) | ✅ |
| Click sidebar `Reports` | ✅ |
| Double-click report tile `Safe Register Journal` (triggers Preview) | ✅ |
| Paste Business Date into config dialog | ✅ |
| Click config `Ok` | ✅ |
| DevExpress Report Preview renders | ✅ |
| Click `Export...` in toolbar | ✅ |
| Export Document dialog opens | ✅ |
| Set `Export format` combo | ⚠️ name fix landed but not yet retested |
| Set `File path` text field | ⚠️ same |
| Uncheck `Open file after exporting` | ⚠️ same |
| Click `OK` to write CSV | ⚠️ same |
| Click `Done` × 2 back to Dashboard | ⚠️ same |

Slice-2 store cycling (HAR → CUL → HAR etc.) is wired up the same way and should also work — the same UIA helpers it uses are proven by the SRJ flow above.

## What still trips it up

1. **State reset between runs.** If a previous trigger left Bravo on Report Preview or the Reports listing, the next trigger fails immediately at "click Reports" because the right-sidebar isn't visible. **Fix:** add a `BackToDashboard()` pre-step at the top of every report module that clicks `Done` (AutoId `btnDone`) until the Dashboard is reached.

2. **Element name discovery is one-shot per screen.** The diagnostic dump truncates Text elements at 40, which sometimes hides the element you need. **Fix:** raise the cap (or remove it) in the diagnostic.

3. **AHK source files cannot contain em-dashes or smart quotes in comments.** I hit this once and the watcher crashed at startup. Stick to ASCII.

## Next-session execution order

**Step 1 — Add `BackToDashboard()` to `lib/Bravo.ahk`:** loop clicking `btnDone` until `Dashboard.Buttons.Reports` element is visible. Add `BackToDashboard()` as first action in every report module's try block. ~15 min.

**Step 2 — Finish SRJ on CUL.** Drop trigger `slice3-srj-cul-6.json`. With the element-name fixes already landed (`Export format` lowercase f, `File path` lowercase p, `Open file after exporting` no "the"), it should run all the way to writing the CSV. If any step fails, the diagnostic logs the visible elements — fix the corresponding entry in `SRJ_ELEMENTS` and re-trigger. Should converge in 2-3 iterations max.

**Step 3 — Multi-store SRJ.** Drop a trigger with `"stores": ["CUL","HAR","LEX","ROA","WAY"]`. Total runtime ~3 minutes (5 stores × ~40s). Result JSON should show 5 success cells.

**Step 4 — Re-point Daily Funds Verification scheduled task.** Skill drops a `safe-register-journal` trigger instead of using computer-use to drive Bravo. ~30 min.

**Step 5 — Build out the other 8 reports.** Each is the same pattern:
1. Copy `reports/SafeRegisterJournal.ahk` to `reports/<NewReport>.ahk`
2. Rename function and slug
3. Update `SRJ_ELEMENTS`-equivalent for the new flow
4. Register handler in `bravo_watcher.ahk` and `bravo_export.ahk`
5. Drop a discovery trigger to find the element names
6. Drop a real trigger, iterate from diagnostics

In priority order: Loans 75-Day, Layaways, Aged Jewelry Markdown, Aged GM Markdown, Employee Activity, Till Register Journal, Chekkit Inactives, Sales by Vendor. Company KPIs is a special case (SSRS browser, not native UI) — likely a direct HTTPS GET rather than UI driving.

Estimated effort: 20-30 minutes per report once the framework is proven on SRJ. Total ~4-5 hours for all 8.

**Step 6 — Re-point the remaining scheduled tasks** (Weekly Loan & Layaway Review, Monday Combined Run, New Inv Weekly Report, Chekkit Tuesday) to use trigger files.

## Files in this session

```
Bravo Data Extraction/
├── lib/
│   ├── UIA-v2/UIA.ahk            ← vendored Descolada UIA-v2
│   ├── Bravo.ahk                  ← UIA helpers + Bravo wrappers
│   ├── StoreCycle.ahk             ← UIA-driven store cycle
│   └── Json.ahk                   ← pure-AHK JSON
├── reports/
│   ├── SafeRegisterJournal.ahk    ← UIA-driven, 95% complete
│   └── UIADiscover.ahk            ← tree-dump helper
├── bravo_watcher.ahk              ← persistent poller
├── bravo_export.ahk               ← manual one-shot
├── config.json
├── README.md
├── FINDINGS_AND_PLAN.md
├── SLICE1_STATUS.md
├── SLICE2_STATUS.md
├── SLICE3_STATUS.md               ← this file
├── CONTINUATION_PLAN.md           ← step-by-step for slice 3+
└── output/uia-tree-2026-05-12.txt ← captured UIA trees from today's session
```

## Lessons added today

- UIA-v2's `elem.Click()` defaults to InvokePattern. WPF tree-view items need `elem.Click("left")` to fire navigation.
- WPF custom controls (like Bravo's Preview/Print labels) may not expose UIA hooks — fall back to double-clicking the list item to trigger the default action.
- AutomationIds are more stable than Names. Bravo's right-sidebar items expose stable IDs like `Dashboard.Buttons.Reports`. Use them when available.
- AHK source files must be ASCII for safety. Em-dashes and smart quotes in comments break the parser.
- Bravo's WPF "right-panel" UI for Preview/Print isn't a real button — the standard list-view "default action" double-click works.
