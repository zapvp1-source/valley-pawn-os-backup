---
name: vp-follower-growth-monthly-check
description: Weekly (Mondays) check of Valley Pawn's social follower growth for the current month via Publer, DM'd to Joshua — tracks whether the QR-sign/giveaway campaign is moving the needle
---

Context: Joshua asked (2026-08-06) to track how Valley Pawn's social follower count does "this month" (August 2026), after we audited the counter-card/QR-sign + $100 monthly giveaway campaign. Baseline captured 2026-08-06 via Publer's Overview dashboard: workspace-wide followers = 6.3K total, and Publer's own "This month" filter showed -2 net for Aug 1-6 (essentially flat/slightly down). Per-account snapshot taken 2026-08-06 (for reference, not to be treated as this month's start-of-month number unless it's the first run of August): Facebook Culpeper 884, Harrisonburg 757, Lexington ~1,600, Roanoke 36, Waynesboro ~1,200, Brand FB 1,700, Instagram @valley_pawn 100, TikTok @thevalleypawn 2, X @valleypawnva 0.

Do NOT use the Meta Graph API, the facebook-post skill, or browser-drive facebook.com/instagram.com for publishing — Publer is the sole publisher (see vp-publer-publisher-only memory). This task is READ-ONLY analytics, so reading Publer's dashboard and reading public profile pages directly (no login/posting) is fine.

Steps each run:
1. Use the Claude-in-Chrome MCP tools (load via ToolSearch if deferred: query "select:mcp__claude-in-chrome__tabs_context_mcp,mcp__claude-in-chrome__navigate,mcp__claude-in-chrome__computer,mcp__claude-in-chrome__browser_batch"). Navigate to https://app.publer.com/#/analytics/overview (Joshua's Chrome session should already be logged into Publer — if not, DM Joshua that Publer needs a fresh login and stop).
2. Set the date-range dropdown (top right) to "This month".
3. Screenshot/read the Followers card (top-left metric: shows current total + a delta badge like "+6" or "-2" for the selected range).
4. Also click through the left sidebar to grab per-account current follower counts if the "Social Accounts" or per-account filter view exposes them (best-effort — the aggregate workspace number is the priority, don't spend excess time here if it's slow to extract).
5. Read/append to a running log file at ~/Documents/Claude/Projects/Refine Social Media/follower_growth_log.csv (columns: date, workspace_followers_total, month_to_date_delta, notes). Create the file with a header row if it doesn't exist yet.
6. If this is NOT the last Monday of the month: send Joshua a SHORT one-line Slack DM (channel D03BHQH5VGT) like: "Follower check (Aug wk N): 6.3K total, +X this month so far." Nothing technical, no follow-up questions.
7. If this IS the last Monday of the month (i.e. adding 7 days would move into the next month): send a fuller Slack DM summarizing the FULL month: total followers start vs end, net change, and a one-line read on whether the QR-sign/giveaway campaign appears to be moving follower counts (compare to the -2 to flat trend seen the first week of August). Also note reach/engagement trend from the same Overview dashboard (those cards sit right next to Followers) since they're a useful leading indicator even when raw follower count is noisy.
8. If Chrome/Publer isn't reachable from this run (no Mac bridge — a known limitation of some cloud-scheduled runs, see enterprise-map memory), do not retry repeatedly; send Joshua one plain DM saying the check needs to run as a local Mac task instead (Settings → this task → run picker → "On your computer"), then stop.

Never post to any public/team channel — Joshua's DM only. Keep every message short — no headers, no bullet essays, just the number and the trend.