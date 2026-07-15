---
name: daily-loan-inventory-text
description: Daily 7:30 AM ET — texts Joshua AND Preston the company Loan Balance and Inventory Balance (all 5 Valley Pawn stores combined) plus the dollar and percent growth of each since the last day of the previous month. Pulls the authoritative Bravo "Company KPI" report via the existing company-kpis pipeline cell (drop trigger → watcher → consolidated xlsx), compares to a self-owned auto-seeding month-end baseline, and sends the result as an iMessage to both recipients (Slack DM fallback for Joshua). ADDITIVE-ONLY: reads/drops into the Bravo Data Extraction pipeline exactly like the other daily tasks; touches no hardened infra.
model: claude-sonnet-5
---

# Daily Loan Balance + Inventory Text

Texts Joshua and Preston one short message every morning:

```
Valley Pawn — Daily numbers
(balances as of 7/13 close)

Loan Balance: $721,4xx  ▲+$3,7xx (+0.5%)
Inventory: $685,9xx  ▲+$2,7xx (+0.4%)

Growth vs 6/30 month-end.
```

Loan Balance and Inventory Balance both come from Bravo's **Company KPI /
Company Performance** report, which reports them "as of yesterday's close" for
all 5 stores combined. Growth is measured against the **last day of the previous
month**, held in a self-owned baseline that auto-seeds on the 1st of each month.

## Recipients (send the SAME text to BOTH)
- **Joshua — iMessage → (804) 930-4221** (+18049304221). Fallback if iMessage fails: Slack DM to `U03BB52MDSA`.
- **Preston — iMessage → (540) 836-4200** (+15408364200). No Slack fallback.

Send to each recipient with a separate `send_imessage` call. If one recipient's
send errors, still send to the other; do not let one failure block the other.

## Key paths
- Task dir: `/Users/joshuadavis/Documents/Claude/Scheduled/daily-loan-inventory-text/`
- Engine: `compute.py` (deterministic parse + baseline + message build)
- Background pull: `daily_run.sh` (health-gate → drop trigger → poll → compute)
- Bravo pipeline: `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/`
- Output xlsx: `.../Bravo Data Extraction/output/<YESTERDAY>_ALL_company-kpis.xlsx`
- Baseline: `baseline/baseline_<YYYY-MM>.json` (month-end the current month is measured against)

## I/O rules (same as every Bravo daily task)
All filesystem I/O against the Bravo Data Extraction folder and the task dir is
OUTSIDE the sandbox — it MUST go through `mcp__remote-devices__Control_your_Mac__osascript`
`do shell script`. Never use the Write tool there. The osascript wrapper kills any
single call running longer than ~25s — keep every in-call `sleep` ≤18s and poll
across SEPARATE calls. Guard `ls`/`cat`/`test` with `|| true`.

## Steps

**1 — Launch the detached pull.**
```
do shell script "cd '/Users/joshuadavis/Documents/Claude/Scheduled/daily-loan-inventory-text'; nohup /bin/bash ./daily_run.sh >/dev/null 2>&1 & echo started"
```
`daily_run.sh` runs the shared `bravo_ensure_healthy.sh` guard, then (retry up to
3x, re-healing between) drops a `company-kpis` trigger for
`<first-of-month>..<yesterday>`, polls for `output/<YESTERDAY>_ALL_company-kpis.xlsx`,
and runs `compute.py`, writing `latest_message.txt` + `latest_status.txt`.

**2 — Poll `latest_status.txt`** in ≤18s sleeps across SEPARATE calls, cap ~25 min:
```
do shell script "cat '/Users/joshuadavis/Documents/Claude/Scheduled/daily-loan-inventory-text/latest_status.txt' 2>/dev/null || true"
```
`RUNNING…` → keep polling. `OK` → step 3. `FAIL …` → step 4.

**3 — Send the text (success).** Read the message:
```
do shell script "cat '/Users/joshuadavis/Documents/Claude/Scheduled/daily-loan-inventory-text/latest_message.txt'"
```
Send that exact text via `mcp__remote-devices__Read_and_Send_iMessages__send_imessage`
to BOTH `(804) 930-4221` and `(540) 836-4200` (one call each). If Joshua's
iMessage errors, fall back to a Slack DM to `U03BB52MDSA`. Do NOT post anywhere
else. If Messages times out, retry once after launching the Messages app.

**4 — On FAIL**, iMessage BOTH recipients a one-liner:
`Valley Pawn daily numbers: couldn't pull Bravo this morning (<reason>). Will retry tomorrow.` Read `run.log` for the reason. Do not loop more than one relaunch
of `daily_run.sh`, then report.

## Baseline behavior (no monthly maintenance needed)
- `compute.py` measures against `baseline/baseline_<current-month>.json`.
- If missing, it seeds from that morning's reading (correct on the 1st, when the
  pull already reflects the prior month-end) with a "baseline seeded today" note.
- July 2026 was pre-seeded from the penny-verified 6/30 Company KPI reading
  (Loan $717,753.48 / Inventory $683,249.66).

## Additive-only guarantee (BUSINESS_OS.md Rule #4)
This task only (a) drops a standard `company-kpis` trigger the pipeline already
supports and (b) reads the resulting xlsx. It never edits `bravo_watcher.ahk`,
`bravo_export.ahk`, any saved Bravo report, any other SKILL.md, or any other
scheduled task. Its baseline and message state live entirely in its own folder.
