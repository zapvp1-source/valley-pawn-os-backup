---
name: daily-loan-inventory-text
description: Daily 7:30 AM ET — texts Joshua AND Preston the company Loan Balance and Inventory Balance (all 5 Valley Pawn stores combined) plus the dollar and percent growth of each since the last day of the previous month. Pulls Bravo's "End of Month" report per store via the pipeline (reliable Reports→Export, NO SSRS date-picker), sums the 5 stores, compares to a self-owned auto-seeding month-end baseline, and iMessages both recipients (Slack DM fallback for Joshua). ADDITIVE-ONLY: drops standard end-of-month triggers into the Bravo Data Extraction pipeline like the other daily tasks; touches no hardened infra.
model: claude-sonnet-5
---

# Daily Loan Balance + Inventory Text

Texts Joshua and Preston one short message every morning:

```
Valley Pawn — Daily numbers
(balances as of 7/14 close)

Loan Balance: $727,414  ▲+$9,661 (+1.3%)
Inventory: $718,724  ▲+$35,474 (+5.2%)

Growth vs 6/30 month-end.
```

## Data source (reliable — no SSRS date-picker)
Bravo's **End of Month** report, one xlsx per store
(`<END>_<STORE>_end-of-month.xlsx`). Each carries **Ending Loan Base** and
**Ending Inventory Base** (dollars) — the SAME metric basis as the Company KPI
Loan Balance / Inventory Balance, so the 6/30 baseline needs no conversion.
Company total = sum of the 5 stores. Window ends **yesterday** (EOM refuses
today/future). This replaced the earlier company-kpis SSRS route, whose
calendar date-picker fails to read the day cell every run (proven 2026-07-14/15).

## Recipients (send the SAME text to BOTH)
- **Joshua — iMessage → (804) 930-4221** (+18049304221). Fallback: Slack DM `U03BB52MDSA`.
- **Preston — iMessage → (540) 836-4200** (+15408364200). No Slack fallback.

Send each with a separate `send_imessage` call; one failing must not block the other.

## Key paths
- Task dir: `/Users/joshuadavis/Documents/Claude/Scheduled/daily-loan-inventory-text/`
- Engine: `compute.py` (parses the 5 EOM xlsx, sums, builds the message)
- Background pull: `daily_run.sh` (health-gate → drop end-of-month trigger for all 5 stores → poll → compute)
- Bravo pipeline: `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/`
- EOM outputs: `.../output/<YESTERDAY>_<STORE>_end-of-month.xlsx`
- Baseline: `baseline/baseline_<YYYY-MM>.json` (month-end the current month is measured against)

## I/O rules (same as every Bravo daily task)
All FS I/O against the Bravo folder and the task dir MUST go through
`mcp__remote-devices__Control_your_Mac__osascript` `do shell script`. The osascript
wrapper kills any single call >~25s — keep in-call `sleep` ≤18s and poll across
SEPARATE calls. Guard `ls`/`cat`/`test` with `|| true`.

## Steps
**1 — Launch the detached pull.**
```
do shell script "cd '/Users/joshuadavis/Documents/Claude/Scheduled/daily-loan-inventory-text'; nohup /bin/bash ./daily_run.sh >/dev/null 2>&1 & echo started"
```
`daily_run.sh` heals Bravo, drops an `end-of-month` trigger for all 5 stores
(window `<first-of-month>..<yesterday>`), polls up to ~24 min for the 5 xlsx
(re-dropping only still-missing stores, up to 3 rounds), then runs `compute.py`
and writes `latest_message.txt` + `latest_status.txt`. A full 5-store EOM run is
~10–15 min.

**2 — Poll `latest_status.txt`** in ≤18s sleeps across SEPARATE calls, cap ~30 min:
```
do shell script "cat '/Users/joshuadavis/Documents/Claude/Scheduled/daily-loan-inventory-text/latest_status.txt' 2>/dev/null || true"
```
`RUNNING…` → keep polling. `OK` → step 3. `FAIL …` → step 4.

**3 — Send (success).** `cat latest_message.txt` and send that exact text via
`send_imessage` to BOTH `(804) 930-4221` and `(540) 836-4200` (one call each).
If Messages times out, launch the Messages app and retry once. If Joshua's
iMessage still errors, Slack-DM `U03BB52MDSA`. Nothing else — no channel posts.

**4 — On FAIL**, iMessage BOTH recipients: `Valley Pawn daily numbers: couldn't
pull Bravo this morning (<reason from latest_status.txt>). Will retry tomorrow.`
Read `run.log` for the reason. One relaunch of `daily_run.sh` max, then report.

## Baseline (no monthly maintenance)
- `compute.py` measures against `baseline/baseline_<current-month>.json`.
- If missing, it seeds from that morning's EOM reading (correct on the 1st, when
  the pull already reflects the prior month-end) with a "seeded today" note.
- July 2026 pre-seeded from the penny-verified 6/30 reading
  (Loan $717,753.48 / Inventory $683,249.66) — EOM basis, so it's directly comparable.

## Additive-only guarantee (BUSINESS_OS.md Rule #4)
Only (a) drops a standard `end-of-month` trigger the pipeline already supports and
(b) reads the resulting xlsx. Never edits `bravo_watcher.ahk`, `bravo_export.ahk`,
any saved report, any other SKILL.md, or any other scheduled task. State lives
entirely in this folder.
