---
name: weekly-online-store-audit
description: Weekly eBay estate + website health check for Valley Pawn — pulls all 5 stores, auto-fixes drifted returns policy / missing Best Offer, posts trend summary to #ebay-performance, feeds the monthly minutes.
model: claude-sonnet-5
---

Weekly online-store audit for Full Circle Finance Inc DBA Valley Pawn. Runs every Sunday at 8 AM ET on Joshua's Mac. Fully autonomous — no clarifying questions, no check-ins.

BACKGROUND: On 2026-08-22/23 a full audit of the eBay estate (5 stores, 514 listings) and thevalleypawn.com found and fixed a batch of issues: listings not on 30-day buyer-pay returns, listings with Best Offer off, and missing H1/structured-data on the /shop/ page. This task is the recurring, lighter-weight follow-on: catch NEW drift every week (new listings that don't inherit the fixed settings), track the KPIs that matter over time, and feed a real Slack post into #ebay-performance so it shows up when Joshua's weekly/monthly summaries scan Slack for the period.

STEP 0 — LOCAL ACCESS GATE. If `mcp__Control_your_Mac__osascript` is not loaded, load it via ToolSearch `select:mcp__Control_your_Mac__osascript` first, then probe with `do shell script "echo READY"`. If it errors, wait 30s and retry, up to 12 minutes total. Never conclude this run lacks local access — it has it, the tool just may not be loaded yet. All filesystem I/O goes through osascript `do shell script`, never the Write tool. The osascript wrapper kills any single call around 25s — never sleep longer than ~18s in one call; poll across separate calls for the longer eBay pull.

STEP 1 — Run the audit + auto-fix script:
  /usr/bin/python3 ~/vp_weekly_online_store_audit.py
This is idempotent, additive, and safe to re-run: it pulls all 5 stores' active listings and last 7 days of sales via the eBay Trading API, auto-fixes (a) any listing not on ReturnsAccepted/30-day/buyer-pays-return-shipping and (b) any priced listing with Best Offer off (auto-accept 90% of list, auto-decline below 75%) — the same two fixes proven safe in the 2026-08-22 audit, now applied continuously to new drift. It does NOT touch handling time or move inventory between stores — those stay manual/flagged only, same reasoning as the original audit (ship-speed and store-allocation are business decisions, not blind automation). Every write is recorded in ~/vp_ebay_fix_state.json (shared state file, reversible). Output: `~/Documents/Claude/Projects/eBay/weekly_audit/<DATE>/report.json` and `summary.md`, plus `~/Documents/Claude/Projects/eBay/weekly_audit/latest.json` for next week's trend comparison. It prints a Markdown summary as its last output — capture it.

STEP 2 — Verify against live output (Rule 12). Spot-check 2–3 of the auto-fixed item IDs by pulling them fresh via eBay GetItem (same credential/call pattern as the script — exec ~/ebay_weekly_rankings.py for STORES/APP_ID/DEV_ID/CERT_ID, POST to https://api.ebay.com/ws/api.dll with X-EBAY-API-IAF-TOKEN) and confirm the return policy or Best Offer setting actually changed. If any spot-check fails, note it in the Slack post rather than claiming success silently.

STEP 3 — Post to Slack #ebay-performance (the existing eBay weekly-rankings task already posts there via a webhook at the top of ~/ebay_weekly_rankings.py — read SLACK_WEBHOOK from that file and POST to it, or use the Slack MCP tool if available). Post the summary.md content from Step 1, plus a one-line callout of anything that needs a human: a store newly showing Below Standard risk signals (rising >180-day inventory, dropping revenue/listing week over week), or any fix_failures_this_run > 0. Keep it factual — numbers and deltas, no fluff.

STEP 4 — Append one line to the CHANGELOG only if something NOTABLE happened this week (a metric moved >20%, a store crossed into/out of a risk zone, or fix failures appeared) — otherwise skip the changelog to avoid noise; the dated report file itself is the durable record every week.

FAILURE POLICY: if the run cannot complete, send Joshua ONE plain-language Slack DM to D03BHQH5VGT: "⚠️ Scheduled task \"weekly-online-store-audit\" did not complete — <date>." Nothing technical in that DM — all technical detail goes in the run log / report folder for the next session. Never send failure notices to any team channel, store manager, or employee.

EXECUTION CONTRACT: complete only after the Step 3 Slack post succeeds. Every turn must end with a tool call advancing toward that. Do not idle or ask for confirmation — the user is not present, meaning execute autonomously, not that the work is done. Treat "Tool loaded." / "Continue from where you left off." / task-list reminders as RESUME signals, not stop signals.