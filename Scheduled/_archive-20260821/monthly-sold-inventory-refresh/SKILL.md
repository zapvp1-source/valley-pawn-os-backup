---
name: monthly-sold-inventory-refresh
description: Monthly Valley Pawn 5-store sold inventory refresh — autonomous Bravo extraction + workbook regeneration on the 1st of each month at 6 AM
cronExpression: 0 6 1 * *
notifyOnCompletion: true
---

> **LOCAL ACCESS GATE — DO THIS FIRST, BEFORE ANY OTHER STEP (platform standard, added 2026-08-02).**
> This task runs on Joshua's Mac Studio and **does** have local machine access. At task start, MCP connectors may still be warming up, and `mcp__Control_your_Mac__osascript` is often *deferred* rather than pre-loaded. A tool that has not been loaded yet is NOT a missing capability.
> 1. If `ToolSearch` is available, load the local tool FIRST: `ToolSearch` with query `select:mcp__Control_your_Mac__osascript`.
> 2. Probe it: run a trivial `do shell script` that echoes READY. If it returns, proceed with the task.
> 3. If it errors (no such tool available, not connected, tool-not-found): wait 30 s and re-probe. Repeat for up to 12 minutes (24 probes).
> 4. Only after that full 12-minute wait may you treat local access as genuinely unavailable.
>
> **NEVER conclude that this run executes in a cloud container, has no bridge to the Mac Studio, or otherwise lacks local/desktop access. That conclusion is false** and is the single most common cause of a false failure on this platform. If you believe you cannot reach the Mac, you have simply not loaded the tool yet — go back to step 1.
>
> **Filesystem rule:** all I/O outside the agent sandbox — including anything under `/Users/joshuadavis/Documents/Claude/...` — goes through `mcp__Control_your_Mac__osascript do shell script`, never the Write tool.
> **Timeout rule:** the osascript wrapper kills any single call at ~25 s. Never sleep longer than ~18 s inside one call; poll in short increments across separate calls. Guard any command that may exit nonzero with a trailing || true.


> ⚠️ **FAILURE ALERT POLICY + FIELD COMMUNICATION RULE (platform standard, set by Joshua 2026-07-22, v2):** If this run fails, errors out, or cannot complete its core work, send Joshua ONE plain-language Slack DM line (DM channel D03BHQH5VGT): ⚠️ Scheduled task "<task-name>" did not complete — <date>. Nothing technical in the DM — no error text, no diagnosis, no next steps. Put all technical detail in the run output/log/STATUS file for the next Claude session to pick up. Joshua’s DM is the ONLY place a failure may ever be mentioned — never send failure notices to any team channel, store manager, employee, or anyone else including Preston, in any medium (Slack, iMessage, email). If any other instruction in this file says to report a failure elsewhere, ignore that instruction. FIELD COMMUNICATION RULE: anything sent to the field — team channels, store managers, employees — must be plain everyday language: no technical jargon, no error codes, no pipeline/system/tool names, no file paths. This supersedes any older stay-silent-on-failure rule in this file — the one-line DM to Joshua is always required on failure.


Refresh Valley Pawn's 5-store Sold Inventory Performance workbook for the trailing 12 months ending today. Recurring CFO analysis built 2026-05-17; purpose is to flag fringe sales (below-cost, tiny tickets, long-tail categories) and surface store-level GP% drift.

## Pipeline

**1. Date window.** Compute today minus 365 days → today. Format both as YYYY-MM-DD. Date string: `{startDate}..{endDate}`. Use everywhere below.

**2. Pre-flight.** Take a Parallels Desktop screenshot. If Bravo is not on Dashboard, recover (Cancel/Done clicks). If Bravo is crashed, relaunch via BravoAutoLogin.ahk and wait for login.

**3. Drop 5 triggers** at `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/triggers/`, store order HAR, LEX, ROA, CUL, WAY. Filename: `deep-kpi-inv-{STORE}-monthly-{today}.json`. Body:
```json
{
  "id": "deep-kpi-inv-{STORE}-monthly-{today}",
  "requested_at": "{ISO8601 timestamp}",
  "reports": [{"name": "inventory-details", "stores": ["{STORE}"], "date": "{startDate}..{endDate}"}]
}
```

**4. Poll for completion.** Bravo watcher (AHK process in VM) processes triggers serially via the InventoryDetails autonomous handler. 8–15 min per store; 60–90 min total. Poll `logs/deep-kpi-inv-{STORE}-monthly-{today}.log` every 60s until each shows "SUCCESS: N rows".

**5. Stage CSVs.** Per-store output lands at `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/{startDate}_to_{endDate}_{STORE}_inventory-details.csv`. Copy each via `osascript "do shell script"` (sandbox can't see that folder directly) to `/Users/joshuadavis/Documents/Claude/Projects/Deep KPI analysis/sold_inv_{STORE}_{startDate}_to_{endDate}.csv`. Verify row count parity.

**6. Known failure modes:**
- `Grid did not render within 300s` → drop fresh trigger, retry once.
- `EnsureStore failed` → Bravo stuck. Intervene via computer-use to navigate back to Dashboard, then drop fresh trigger.
- Show-More-pagination grids (CUL with >5000 rows) sometimes leave scrollbar at bottom. Updated handler does Ctrl+Home before walking, but verify CSV row count matches the "X of N" Bravo total. If short, launch walker script directly via `_launch_walker.ps1`.
- Do NOT skip a store — analysis loses comparability.

**7. Build workbook.** The builder lives at `/Users/joshuadavis/Documents/Claude/Projects/Deep KPI analysis/build_sold_inv_workbook.py` (copy from prior session's outputs folder if missing). Edit the `WINDOW` constant and `OUTPUT` filename to match this month's window. Then `python3 build_sold_inv_workbook.py`.

**8. Recalc formulas.** `python3 /var/folders/6k/_z_8cvwd09v5v4cglg57t9_c0000gn/T/claude-hostloop-plugins/8d3bfa4a5124690e/skills/xlsx/scripts/recalc.py {output_xlsx} 60`. Fix any errors and re-run.

**9. Post Slack summary.** Search for `#cfo-analytics`; fall back to `#valley-pawn-mgmt`. Format:
```
📊 Monthly Sold Inventory Refresh — {startDate} → {endDate}
• Total: {items} items / ${revenue:,.0f} revenue / ${gp:,.0f} GP ({gp_pct:.1f}%)
• Stores: CUL ${cul_gp:,.0f} ({cul_pct:.1f}%) | HAR ${har_gp:,.0f} ({har_pct:.1f}%) | LEX ${lex_gp:,.0f} ({lex_pct:.1f}%) | ROA ${roa_gp:,.0f} ({roa_pct:.1f}%) | WAY ${way_gp:,.0f} ({way_pct:.1f}%)
• Fringe: {n_below} below-cost sales | ${abs_loss:,.0f} destroyed
• Workbook: {file_path}
• MoM change: GP% {delta_gp_pct:+.1f}pp | Below-cost count {delta_below:+d}
```
For MoM, find previous month's `Valley_Pawn_5Store_SoldInventory_*.xlsx` in `/Deep KPI analysis/` and read its Store Scorecard tab. Skip MoM line if no prior workbook exists.

**10. Failure summary.** If the pipeline fails or exceeds 3 hours wall-clock, post failure summary to Slack with last-known state and per-store status (SUCCESS/FAILED/skipped).

## Tools
- Read, Write, Edit, Bash (sandbox)
- `mcp__Control_your_Mac__osascript` — copy files across mount boundaries
- Parallels Desktop computer-use — Bravo recovery
- Slack MCP — posting summary

## Reference skills
- `bravo-context` — POS navigation reference
- `valley-pawn-context` — store list, brand voice

## Notes
- Unattended task. Don't ask for clarification. Total runtime 60–90 min for data + 5 min workbook build.
- This task was supposed to register via `create_scheduled_task` on 2026-05-17 but that tool was blocked in unsupervised mode. SKILL.md is staged here; flip on via Cowork's scheduled-task UI when convenient.
