---
name: monthly-sold-inventory-refresh
description: Monthly Valley Pawn 5-store sold inventory refresh — autonomous Bravo extraction + workbook regeneration on the 1st of each month at 6 AM
cronExpression: 0 6 1 * *
notifyOnCompletion: true
---

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
