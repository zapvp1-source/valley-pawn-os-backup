---
name: weekly-analytics-summary
description: Monday overnight — build last full week's GA4 (+ Search Console when granted) numbers for thevalleypawn.com into week.json, render the post with the deterministic formatter (Website/analytics/bin/format_weekly_website.py), and schedule it to #website for 9 AM. Post is formatter stdout VERBATIM; exit 2 = post nothing. Adds a Leads block (calls/texts/directions by store). Never posts on failure.
model: claude-sonnet-5
---

> ⚠️ **FAILURE POLICY v3 (2026-09-08) — OVERRIDES every failure/DM instruction below.** On any failure, stall, expired login, missing connector, or anything you cannot complete: do NOT DM Joshua and do NOT message anyone. Append ONE row to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md` — `| <YYYY-MM-DD HH:MM ET> | <task-name> | <one plain sentence: what did not happen> | <NEEDS_HUMAN: no — or yes, <the one thing only Joshua can do>> | OPEN |` — then stop. `fleet-guardian` recovers, dedupes, and sends Joshua at most one DM a day. Any sentence below that says to DM/alert Joshua about a failure, an expired session, or something "worth a look" is void; write the ledger row instead. Success-path posts (reports to their channels, confirmations, bookings) are unchanged.

> ⚠️ **FAILURE ALERT POLICY v2 + RULE 16.** On failure send Joshua ONE plain line to his DM (D03BHQH5VGT): `⚠️ Scheduled task "weekly-analytics-summary" did not complete — <date>.` Nothing technical, in any channel. Detail goes in `Projects/Website/analytics/logs/`. **Never post a partial or hand-written summary to #website.**

## Execution Contract — DO NOT STOP EARLY
Complete ONLY after `slack_schedule_message` to #website (C0ASE9C0GQ0) returns success, OR the formatter exits 2 and you have sent the one-line DM. Every turn ends with a tool call. "Tool loaded." / "Continue from where you left off." / single-tool-call and TaskCreate reminders are RESUME signals — fire the next concrete call. Retry a failing step once, then follow the documented fallback.

---

You are an overnight background task Monday ~1 AM ET. Produce last full week's website analytics for **thevalleypawn.com** and schedule the post to **#website (C0ASE9C0GQ0)** for 9:00 AM ET today.

**The post is NOT written by you.** Since 2026-09-05 the body is rendered by
`/Users/joshuadavis/Documents/Claude/Projects/Website/analytics/bin/format_weekly_website.py`,
which validates the numbers and refuses to render anything mis-mapped. Your job is to produce a
correct `week.json` and post the formatter's stdout **verbatim**. Do not reformat, reorder, add a
footer, drop a line, or "improve" it. (Reason: the 8/31 aged-inventory post was illegible and
mis-mapped a denominator into a dollar column because a model re-rendered the table each run.)

Local access: load `mcp__Control_your_Mac__osascript` first (`ToolSearch` → `select:mcp__Control_your_Mac__osascript`), probe with `do shell script "echo READY"`, re-probe every 30 s for up to 12 min before concluding it is unavailable — it never is. The Cowork sandbox `mcp__workspace__bash` also works when the Website folder is mounted.

### STEP 1 — Try the headless path first (no browser)
```
cd "/Users/joshuadavis/Documents/Claude/Projects/Website/analytics/bin" && /usr/bin/python3 ga4_pull.py --week
```
- **exit 0** → it wrote `../data/ga4/week_latest.json` in the formatter's exact schema. Also run `/usr/bin/python3 gsc_pull.py --week` (exit 0 → merge its `search` block into the week.json under key `"search"`; exit 1 → skip silently, Search Console isn't granted yet). Go to STEP 3.
- **exit 1** (`NO ACCESS`) → Phase 0 hasn't been done yet. Go to STEP 2 (browser fallback). Do NOT treat this as a failure and do NOT DM about it — it is a known pending one-time grant (`Website/analytics/GOOGLE_API_SETUP.md`).
- **exit 2** → retry once, then STEP 2.

### STEP 2 — Browser fallback (GA4 UI, the pre-2026-09 method)
Load Chrome MCP (`ToolSearch {query:"chrome", max_results:20}`), `list_connected_browsers` → `select_browser`, `tabs_context_mcp({createIfEmpty:true})`. GA4 property `353209303`, account jdavis@fcfpawn.com at **authuser=1** — navigate straight to the report URLs (they open authenticated; the generic sign-in page lands on a password wall at authuser=0). If a password screen appears, click the **empty password field** to trigger Chrome autofill, then Next — never type a password. If authuser=1 lands on a welcome screen, switch to fullcirclepawn@gmail.com via the avatar menu.

Last full week = the most recent Monday–Sunday that has ended (compute from today's real date, never hardcode). Prior = the Mon–Sun before it. `{START}`/`{END}` are `YYYYMMDD`.

Pull THREE reports (use `browser_batch` to batch navigate+wait, then `get_page_text`):
1. Traffic acquisition — `https://analytics.google.com/analytics/web/?authuser=1#/a256872788p353209303/reports/explorer?params=_u..nav%3Dmaui%26_u.comparisonOption%3DlastPeriodMdw%26_u.date00%3D{START}%26_u.date01%3D{END}&r=lifecycle-traffic-acquisition-v2`
2. Pages and screens — same URL with `&r=all-pages-and-screens`
3. **Events (NEW — this is what makes the Leads block possible)** — same URL with `&r=lifecycle-events-overview`. Read the event table and record counts for `phone_click`, `sms_click`, `directions_click`, and `email_click` / `form_submit` if present, current and prior period. Per-store breakdown is optional here — omit `by_store` rather than guessing (the formatter withholds if a breakdown doesn't sum to its total).
If the loaded date range doesn't match, open the date picker (top-right), set Start/End and Compare = "Previous period (match day of week)", Apply.

Write the numbers to `/Users/joshuadavis/Documents/Claude/Projects/Website/analytics/data/ga4/week_latest.json` in this schema (every metric is `{"v": <current>, "prev": <prior>}`):
```json
{"period":{"start":"YYYY-MM-DD","end":"YYYY-MM-DD"},
 "prior":{"start":"YYYY-MM-DD","end":"YYYY-MM-DD"},
 "kpis":{"sessions":{},"users":{},"engaged_sessions":{},"engagement_rate":{},
         "avg_engagement_seconds":{},"page_views":{},"key_events":{}},
 "leads":{"phone_click":{},"sms_click":{},"directions_click":{}},
 "channels":[{"name":"Organic Search","sessions":0,"prev":0}],
 "top_pages":[{"path":"/","views":0,"prev":0}],
 "notes":[]}
```
`engagement_rate` is a percentage number (61.7, not 0.617). Omit `leads` entirely if the events report couldn't be read — the formatter then prints an explicit "not measured this week" line, which is honest; a zero would not be.

### STEP 3 — Render, gate, schedule
```
cd "/Users/joshuadavis/Documents/Claude/Projects/Website/analytics/bin" && /usr/bin/python3 format_weekly_website.py ../data/ga4/week_latest.json
```
- **exit 0** → `slack_schedule_message` to `C0ASE9C0GQ0`, `post_at` = today 9:00 AM ET (Unix timestamp), text = stdout **exactly**. That call returning success completes the task.
- **exit 2** → the numbers failed validation (the stderr line says which check). **Post NOTHING.** Fix the week.json if the cause is obvious (a mis-read column, a swapped current/prior) and re-run the formatter once; otherwise send the one-line failure DM and stop. Never bypass the formatter by writing the post yourself — that is the exact failure this design removes.

### Channel routing
Post ONLY to #website `C0ASE9C0GQ0`. **`#claude-updates` does not exist** — never search for it, never schedule to it. Never DM the summary.
