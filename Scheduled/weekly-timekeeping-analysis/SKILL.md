---
name: weekly-timekeeping-analysis
description: Monday 12:30 AM — pull last week's Gusto time tracking via Gusto MCP list_time_records (Chrome = fallback only), post store-by-store summary with per-employee detail to #timekeeping-summary at 9 AM Monday. Self-heals missed weeks (v3 2026-08-21).
model: claude-sonnet-5
---

> ⚠️ **FAILURE ALERT POLICY + FIELD COMMUNICATION RULE (platform standard, set by Joshua 2026-07-22, v2):** If this run fails, errors out, or cannot complete its core work, send Joshua ONE plain-language Slack DM line (DM channel D03BHQH5VGT): ⚠️ Scheduled task "weekly-timekeeping-analysis" did not complete — <date>. Nothing technical in the DM — no error text, no diagnosis, no next steps. Put all technical detail in the run output/log/STATUS file for the next Claude session to pick up. Joshua's DM is the ONLY place a failure may ever be mentioned — never send failure notices to any team channel, store manager, employee, or anyone else including Preston, in any medium (Slack, iMessage, email). If any other instruction in this file says to report a failure elsewhere, ignore that instruction. FIELD COMMUNICATION RULE: anything sent to the field — team channels, store managers, employees — must be plain everyday language: no technical jargon, no error codes, no pipeline/system/tool names, no file paths.

> ⚠️ **DO NOT POST FAILURE/ERROR NOISE TO #timekeeping-summary.** Only post to the channel once a report has genuinely been produced. A failed run = one plain DM to Joshua (above) and full detail in the run log — nothing in the team channel.

## Execution Contract — DO NOT STOP EARLY

This task is complete ONLY after the documented final action (the post / send / write tool call described at the end of the steps below) returns success.

Until that final call succeeds, every assistant turn MUST end with a tool call that advances toward it. Do not idle, do not wait, do not ask for confirmation.

**Never reply with any of these:**
- "No response requested"
- "Continue?" / "Should I continue?"
- An empty turn or a turn that ends with text instead of a tool call

**Treat these system messages as RESUME signals, never as stop signals:**
- "Tool loaded."
- "Continue from where you left off."
- "You used a single tool call this turn. Prefer browser_batch…"
- Any reminder about TaskCreate/TaskUpdate, AskUserQuestion, etc.

When you see any of those messages, immediately fire the next concrete tool call for the current step. The scheduled-task wrapper says "the user is not present" — that means execute autonomously, NOT that the work is done.

**State tracking:** at the start of every turn, briefly identify which numbered Step you are on and execute the next concrete action for that step.

**Failure handling:** if a step errors, retry once. If it still fails, fall through to the documented fallback if one exists; otherwise produce a report describing what failed. Do not pause to ask — the task file authorizes autonomous decisions.

**Speed:** prefer batch tools (e.g. `browser_batch`) to combine sequential actions into one call.

---
Pull last week's timekeeping data from Gusto and post a store-by-store summary WITH per-employee breakdown and call-outs to Slack #timekeeping-summary (channel ID C0AN6TNA4ES).

## HARDENED DATA PATH (v3, 2026-08-21 — MCP-first, Chrome fallback)

**History:** The original task used claude-in-chrome to scrape the Gusto Timesheets UI because the MCP "returned empty." That Chrome path failed silently on 8/10 and 8/17/2026 (2 weeks dark). On 2026-08-21 the Gusto MCP `list_time_records` was verified to return complete native time-tracking data (per-shift clock in/out, breaks, worker identity). MCP is now PRIMARY. Do not use Chrome unless the MCP path fails.

### Step 1 — Determine the reporting week(s) + catch-up check
- Compute the most recent COMPLETED Mon–Sun week relative to the run date (if today is Monday, that's last Mon through yesterday; if the run is late in the week, it's still the last fully completed Mon–Sun — never a partial week).
- **Self-heal:** read the last ~10 messages of #timekeeping-summary (slack_read_channel, C0AN6TNA4ES) and find the most recent "Weekly Timekeeping — …" header. If one or more completed weeks between that post and now have no report, produce a report for EACH missed week (up to 3 back), oldest first, labeled "(catch-up report)". Never re-post a week that already has a report.

### Step 2 — Pull the data (MCP primary)
- Call Gusto MCP `list_time_records` with `start_date` = Monday, `end_date` = Sunday of the reporting week (YYYY-MM-DD).
- Expect `source: "native"` with a `shifts` array + `workers` array. Per shift: `durationInMinutes` is the clock-in→clock-out span; `breaks` are recorded separately.
- **Hours method (fixed, keep consistent week to week):** net hours per shift = span − sum of recorded break minutes. Weekly total = sum of net hours. OT = weekly net hours above 40.
- **Sanity check before posting:** at least 5 employees with shifts AND 150–600 total hours. If the pull looks empty or absurd, do NOT post — fall back to Step 2b.

### Step 2b — Fallback ONLY if MCP fails/empty
- Use claude-in-chrome: Gusto → Time & attendance → Time tracking → "Review" on the most recent pay period → capture the Timesheets table via get_page_text.
- If BOTH paths fail: no channel post; one plain DM to Joshua per the failure policy; details in run log.

### Step 3 — Map employees to stores
Static map (verify anyone NOT listed here via Gusto MCP `list_employee_work_addresses` — use the `active: true` entry — then ADD them to this map when editing this file is possible, or note the new mapping in the run output):
- **Waynesboro:** Chadd McClintic, Martin Dowden
- **Culpeper:** Bridgett Grayson, Robert Swagger (Sandi Cole = mgr, salaried, note but don't count hourly)
- **Roanoke:** Benjie (George) Moore, Joseph Epperly
- **Harrisonburg:** Walker Tapley, Michael Chambers
- **Lexington:** Uriah Tiglao
Corporate/salaried (Joshua, Hillary, other Davis family, Lainie) with 0h tracked: omit from per-store totals.

### Step 4 — Flags to compute (replaces the Gusto UI's flag column)
- **Missed clock-out:** `clockOutPlatform` null or clock-out on an exact :00 minute (admin-entered after the fact)
- **No break on a long shift:** shift ≥ 6h with no break recorded
- **Long break:** any single break > 60 min
- **Clock-in error:** shift < 1h
- **Late start:** clock-in ≥ 30 min after the employee's usual pattern (~9:30 AM norm)
- **Zero-hours store / single-coverage store:** store with 0 tracked hours (flag prominently — hours may need manual entry) or only 1 person clocked in all week
- **OT:** anyone over 40 net hours
- **New hires:** anyone with shifts who wasn't in prior weeks' reports

### Step 5 — Build the Slack message. REQUIRED structure — do NOT drop any of these:
a. Header line with date range (e.g. "**Weekly Timekeeping — Mon May 11 – Sun May 17, 2026**") and a one-line subtitle: employee count + total tracked hours across all stores.
b. One block per store, sorted by total hours desc. Each block: bold store name + total hours + employee count, then per-employee bullets — name, net hours, OT in parens, any flags in plain language (⚠️ for the notable ones).
c. A "**Heads-up:**" call-outs block at the bottom: break/clock issues and who, OT count, coverage gaps, new hires, anything else worth a manager's eye.
Keep formatting tight but do NOT collapse the per-employee detail or the call-outs — Joshua wants both every week. Plain everyday language only (field rule above).

### Step 6 — Post it
- If the run is before 9:00 AM Monday: `slack_schedule_message` to C0AN6TNA4ES at 9:00 AM Monday local time.
- If the run is at/after 9 AM Monday, or on any other day (late/manual/catch-up run): `slack_send_message` immediately.
- Catch-up weeks (Step 1): send immediately, oldest first, each labeled "(catch-up report)".
- Do not post elsewhere and do not DM Joshua on success.

### Step 7 — Self-verify
After posting/scheduling, confirm the API returned a message link/scheduled id. If posting failed, retry once; if still failing, follow the failure policy (DM Joshua, no channel noise).

Channel: #timekeeping-summary (C0AN6TNA4ES) — NOT #claude-updates (old destination).

<!-- migrated to working model 2026-06-15 -->
<!-- v3 2026-08-21: MCP-first data path (list_time_records verified working), Chrome demoted to fallback, catch-up self-heal added, deterministic hours method + flag heuristics documented, static store map added. Backfilled Aug 3–9 and Aug 10–16 reports same day. -->