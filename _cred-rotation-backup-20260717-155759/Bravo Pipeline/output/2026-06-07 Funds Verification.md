# Daily Funds Verification — 2026-06-07

**Bottom line:** all 5 matched. No funds activity Sunday — banks closed, zero Slack sends, zero BANK→Safe transfers in any store's journal.

## Reconciliation

| Store | Sent (Slack ledger) | Entered to Safe (Bravo) | Status |
|---|---|---|---|
| CUL | $0 | $0 | ✓ Matched |
| HAR | $0 | $0 | ✓ Matched |
| LEX | $0 | $0 | ✓ Matched |
| ROA | $0 | $0 | ✓ Matched |
| WAY | $0 | $0 | ✓ Matched |

## Source data

- Slack: all 5 funds channels (#pepper-funds, #lex-funds, #boro-funds, #roanoke-funds, #harrisonburg-funds) empty for the 2026-06-07 00:00–24:00 ET window.
- Bravo CSVs: `Bravo Data Extraction/output/2026-06-07_{CUL,HAR,LEX,ROA,WAY}_safe-register-journal.csv` — 5 rows each, no rows matching the funds-sent signature (Txn Type=TENDER TRANSFER, Till Number=BANK, Tender Type=Cash, Amt Coll negative).

## Pipeline notes — patch validation

This run doubles as the validation of the SafeRegisterJournal CS-toggle patch deployed today.

**Before (2026-06-06 run):**
- 3 trigger drops required
- CUL, HAR, ROA all timed out with "Preview did not render within 30s (Export Document button never appeared)"
- Cascade failures into stores that couldn't recover BackToDashboard
- Total ~25 min to land all 5 CSVs

**After (this run):**
- 1 trigger drop
- 5/5 SUCCESS on first attempt
- Every cell hit `[pre-export] Continuous Scrolling is ON — calling Toggle() to flip state` → `post-toggle state = 0`
- Consistent ~62-64 seconds per cell
- Total ~6 min for the whole 5-store cycle

The pipeline is now consistent for the team.

## Deployment record

- Handler: `Bravo Data Extraction/reports/SafeRegisterJournal.ahk` — patched 2026-06-08 ~11:28 EDT
- Backup: `Bravo Data Extraction/reports/SafeRegisterJournal.ahk.bak-pre-cs-toggle-2026-06-08`
- Island source: `Bravo Pipeline/island/source/SafeRegisterJournal_island.ahk`
- Island PoC doc: `Bravo Pipeline/island/proof-of-concept/safe-register-journal-cs-fix.md`
- Watcher restarted via `_restart_watcher.ps1` (Y:-aware) at 2026-06-08 14:48:45 — triggered by one-shot scheduled task `srj-watcher-restart-oneshot-2026-06-08` because prlctl exec hung from the interactive osascript session (BRAVO_KNOWN_ISSUES.md terminal-grab issue).
