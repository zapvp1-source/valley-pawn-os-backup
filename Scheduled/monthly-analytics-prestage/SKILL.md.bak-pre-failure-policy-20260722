---
name: monthly-analytics-prestage
description: Last-day-of-month 8 PM — pre-stage the 6 EOM date-window XLSX files the monthly-analytics-report task will read at 3 AM on the 1st. Drops 6 triggers to the Bravo Data Extraction pipeline (one per date window, all 5 stores) and copies each window's CSVs to a window-tagged sidecar so the same-End-date overwrites don't stomp each other. Silent on failure.
model: claude-sonnet-5
---


---
name: monthly-analytics-prestage
description: Pre-stage the 6 End-of-Month date-window CSVs that `monthly-analytics-report` consumes at 3 AM on the 1st. Drops 6 pipeline triggers (one per window, all 5 stores) and copies each window's CSVs to window-tagged sidecar files. Silent on failure (no DMs, no Slack posts).
---

> ⚠️ **FAILURE POLICY — silent on failure.** Never DM. Never post a failure notice to Slack. If the pipeline can't produce some windows in time, save the markdown working file and exit silently. The downstream `monthly-analytics-report` (3 AM) and `monthly-analytics-watchdog` (7 AM) handle the consequences.

You are pre-staging the Bravo End-of-Month CSVs the `monthly-analytics-report` task will read tomorrow at 3 AM.

# Step 0 — Last-day-of-month gate

This task is scheduled `0 20 28-31 * *` (8 PM on days 28, 29, 30, 31). Most months it fires once; February it fires once. Always check at the top:

```bash
osascript -e 'do shell script "tomorrow=$(date -v+1d +%d); if [ \"$tomorrow\" = \"01\" ]; then echo PROCEED; else echo SKIP; fi"'
```

If output is `SKIP`, exit silently — this isn't actually the last day of the month. If `PROCEED`, continue.

# Step 1 — Connector readiness gate

Confirm `mcp__Control_your_Mac__osascript` is loaded (probe with `do shell script "echo READY"`). If still warming, wait 30 s × up to 12 min. Connector warmup is NOT failure.

# Step 2 — Compute the 6 date windows

Report month = current month (we're staging on the last day, so "the month that's ending tonight"). Compute:

| Window key | Start | End |
|---|---|---|
| same-month-current | first of report month | last of report month |
| same-month-prior | same window, year − 1 | same window, year − 1 |
| ytd-current | Jan 1 of report year | last of report month |
| ytd-prior | Jan 1 of prior year | last of report month, prior year |
| t12m-current | last of report month minus 12 months + 1 day | last of report month |
| t12m-prior | one year earlier than t12m-current | one year earlier than t12m-current |

For T12M Prior: if start < `2024-06-03` (Bravo calendar floor verified 2026-06-04), clamp start to `2024-06-03` and note the actual start that comes back in the CSV header.

Format dates as `YYYY-MM-DD`. Pipeline range syntax is `YYYY-MM-DD..YYYY-MM-DD`.

# Step 3 — Build the sidecar folder

```bash
osascript -e 'do shell script "mkdir -p \"/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/monthly-analytics/$(date +%Y-%m)\""'
```

Where `$(date +%Y-%m)` is the report month (e.g. `2026-06`).

# Step 4 — Drop 6 triggers, one per window, serially

The pipeline's `end-of-month` cell handler is `EndOfMonth.ahk` (verified 2026-06-10). Its trigger schema is the same one `daily-funds-verification` uses, with `name: "end-of-month"` and `date` either `YYYY-MM-DD` (single day) or `YYYY-MM-DD..YYYY-MM-DD` (range). XLSX output: `output/{END_DATE}_{STORE}_end-of-month.xlsx`.

For each window IN ORDER (same-month-current first because its CSVs land first and we copy them aside before the same End date gets reused by ytd-current and t12m-current):

1. **Trigger ID:** `monthly-analytics-prestage-{window-key}-{YYYY-MM-DDTHH-MM-SS}` derived from osascript `date`.

2. **Trigger JSON** (write to `triggers/` via osascript heredoc — NEVER use the Write tool against this folder):

```bash
osascript -e 'do shell script "cat > \"/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/triggers/{TRIGGER_ID}.json\" <<EOF
{
  \"id\": \"{TRIGGER_ID}\",
  \"requested_at\": \"{ISO8601}\",
  \"reports\": [
    {\"name\": \"end-of-month\", \"stores\": [\"CUL\",\"HAR\",\"LEX\",\"ROA\",\"WAY\"], \"date\": \"{START}..{END}\"}
  ]
}
EOF"'
```

Use the exact key names — a malformed trigger gets silently renamed `untitled_*` and never runs.

3. **Poll for result.** Each cell takes ~60–90 s, 5 stores serial per trigger → ~5–8 min per window. Poll `results/{TRIGGER_ID}.result.json` every 18 s (per the osascript wrapper's ~25 s timeout — see `daily-funds-verification` Step 0c).

```bash
osascript -e 'do shell script "[ -f \"/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/results/{TRIGGER_ID}.result.json\" ] && echo READY || echo WAITING"'
```

Hard timeout per window: 12 minutes. If exceeded, skip to the next window — don't block.

4. **Copy each successful CSV to the sidecar.** As soon as the result JSON appears (or a per-store CSV ≥ 2 KB shows up), copy the 5 CSVs to the window-tagged sidecar:

```bash
osascript -e 'do shell script "for store in CUL HAR LEX ROA WAY; do
  src=\"/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/{END_DATE}_${store}_end-of-month.xlsx\"
  dst=\"/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/monthly-analytics/{YYYY-MM}/{WINDOW_KEY}_${store}.xlsx\"
  if [ -s \"$src\" ] && [ $(stat -f%z \"$src\") -gt 2048 ]; then cp \"$src\" \"$dst\"; fi
done"'
```

The `[ -s ]` + size check prevents copying the 0-byte stub the watcher leaves on failed cells.

5. **Iterate-to-fix on failure.** If a window's result JSON came back with `status="error"` cells, or specific store CSVs are missing/0 bytes:
   - Drop a focused retry trigger for just the failing stores with `-retry-1` suffixed to the trigger ID
   - Poll again with a 12-min timeout
   - If retry also fails, move on to the next window — don't keep retrying indefinitely

If the watcher itself looks hung (trigger sits in `triggers/` for > 2 minutes unclaimed), reuse the silent watcher-restart pattern from `daily-funds-verification` Step 2e (one-shot scheduled task running `_restart_watcher.ps1` via `prlctl exec`).

# Step 5 — Total time budget

Hard ceiling: 90 minutes (6 windows × ~8 min plus retries). If the budget is exhausted with windows still missing, save the working file and exit silently. The watchdog at 7 AM tomorrow will surface the gap.

# Step 6 — Save the working file

Write a markdown summary at `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/monthly-analytics/{YYYY-MM} Prestage.md`:

```
# Monthly Analytics Prestage — {YYYY-MM}

**Status:** {COMPLETE 30/30 | PARTIAL X/30 | FAILED}

## Windows
| Window | Range | CSVs |
|---|---|---|
| same-month-current | YYYY-MM-DD..YYYY-MM-DD | 5/5 |
| same-month-prior   | ... | 5/5 |
| ytd-current        | ... | 5/5 |
| ytd-prior          | ... | 5/5 |
| t12m-current       | ... | 5/5 |
| t12m-prior         | YYYY-MM-DD..YYYY-MM-DD | 5/5  *(clamped — actual start YYYY-MM-DD if Bravo floor hit)* |

## Sidecar
`/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/monthly-analytics/{YYYY-MM}/`
Lists each window×store file with size.

## Notes
{Any retries, hangs, clamps, or anomalies.}

_Generated {YYYY-MM-DD HH:MM} ET._
```

# Hard rules

- All I/O against `Bravo Data Extraction/` MUST go through `osascript do shell script` — the folder is outside the file-tool sandbox.
- No DMs. No Slack posts on failure. Only the working file records what happened.
- This task is ADDITIVE — never modify `EndOfMonth.ahk`, `bravo_watcher.ahk` dispatch, the saved Bravo "End of Month" report, or any other production scheduled task.
- Do not run on days where tomorrow isn't the 1st (Step 0 gate).

<!-- migrated to working model 2026-06-15 -->