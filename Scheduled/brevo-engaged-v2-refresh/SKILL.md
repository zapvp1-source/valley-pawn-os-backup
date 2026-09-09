---
name: brevo-engaged-v2-refresh
description: Wednesdays 6:20 AM — rescore the email audience from real per-contact click behavior and refresh Brevo list 19 (Engaged v2, human-verified). Runs alongside list 7; does not change what any campaign sends to. Silent unless membership moved materially.
model: claude-sonnet-5
---

> ⚠️ **FAILURE POLICY v3 (2026-09-08) — OVERRIDES every failure/DM instruction below.** On any failure, stall, expired login, missing connector, or anything you cannot complete: do NOT DM Joshua and do NOT message anyone. Append ONE row to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md` — `| <YYYY-MM-DD HH:MM ET> | <task-name> | <one plain sentence: what did not happen> | <NEEDS_HUMAN: no — or yes, <the one thing only Joshua can do>> | OPEN |` — then stop. `fleet-guardian` recovers, dedupes, and sends Joshua at most one DM a day. Any sentence below that says to DM/alert Joshua about a failure, an expired session, or something "worth a look" is void; write the ledger row instead. Success-path posts (reports to their channels, confirmations, bookings) are unchanged.

> **LOCAL ACCESS GATE — DO THIS FIRST.** This task runs on Joshua's Mac Studio and has local machine access. If `ToolSearch` is available, load `select:mcp__Control_your_Mac__osascript` first, then probe with `do shell script "echo READY"`. If it errors, wait 30 s and re-probe, up to 12 minutes. NEVER conclude this run lacks local access — that conclusion is false. All file I/O under `/Users/joshuadavis/Documents/Claude/...` goes through osascript `do shell script`, never the Write tool, never `request_cowork_directory`. The osascript wrapper kills any single call at ~25 s — never sleep more than ~20 s in one call; poll across separate calls.

## Execution Contract — DO NOT STOP EARLY
Complete ONLY after the Step 4 EFFICIENCY_LOG write succeeds. Every turn until then must end in a tool call. Never reply "No response requested", never ask "Continue?", never end a turn with text only. Treat "Tool loaded." / "Continue from where you left off." / any task-tool reminder as RESUME signals. "The user is not present" means execute autonomously.

## Rule 16 / Rule 18 — hard
No failure notices, no technical jargon, no file paths, no tool or endpoint names in ANY Slack message including Joshua's DM. If this run cannot finish, write the detail to the EFFICIENCY_LOG and stop silently. This task is normally SILENT on Slack — see Step 3 for the one exception.

---

# brevo-engaged-v2-refresh

**Why this exists (Email Dept plan `Email Refinement/19_EMAIL_DEPT_AUTOMATION_PLAN_2026-09-05.md`, Phase 1 item 9):** Brevo list 7 ("Engaged List") is fed by a rule that adds anyone who clicks any link. Security scanners click every link the instant mail lands, so list 7 has been recruiting machines — which is why some sends have reported more clickers than recipients. On 2026-09-05 a first scoring pass found that of 177 contacts on list 7, only **87** show human-shaped intent clicks; 90 were stale (no click in 90 days) or scanner-shaped.

**List 19 — "Engaged v2 — human-verified"** is the clean parallel audience. It is maintained ONLY by this task. Nothing sends to it yet; list 7 remains the live weekly audience until Joshua's go. This task's job is to keep list 19 accurate and to log the week-over-week comparison so that decision has real evidence behind it.

**All logic lives in one script — do not re-implement it:** `/Users/joshuadavis/Documents/Claude/Projects/Email Refinement/bin/engaged_v2.py` (docstring documents the scoring rule, the tiered universe, and the rotating slice). State: `bin/engaged_v2_state.json`.

## Step 1 — Run the refresh
```
cd '/Users/joshuadavis/Documents/Claude/Projects/Email Refinement/bin'
(nohup python3 -u engaged_v2.py --apply --compare --max-universe 1200 > /tmp/ev2_weekly.log 2>&1 &)
```
It takes roughly 15–20 minutes (about one second per contact). Poll `tail -6 /tmp/ev2_weekly.log` every ~20 s across separate osascript calls until the log ends in `DONE` — check with `pgrep -f engaged_v2 >/dev/null && echo RUNNING || echo DONE`. Do not start a second copy; if one is already running when you begin, wait for it instead.

## Step 2 — Verify against reality, not the script's own output (Rule 12)
Independently re-read the list from Brevo and confirm the count matches what the script reported:
`GET https://api.brevo.com/v3/contacts/lists/19/contacts?limit=500` (header `api-key:` = contents of `~/.config/valley-pawn/brevo_api_key`). Also re-read list 7's count. If the two counts disagree with the log, trust Brevo and say so in the log.

## Step 3 — Slack: normally silent
Post nothing in a normal week. Post ONE plain-language line to `C0APR5WUL2Z` (#email-campiagns — the channel name really is spelled that way) ONLY if the human-verified audience moved by more than 15% versus last week's `last_count` in the state file:
`📇 Email audience check: <N> customers now clicking through on their own, <up/down> from <M> last week.`
No list numbers, no tool names, no mechanism. Nothing else, ever.

## Step 4 — Log (always, even if the run failed)
Append to `/Users/joshuadavis/Documents/Claude/Projects/Email Refinement/EFFICIENCY_LOG.md` via an osascript heredoc:
```
## <YYYY-MM-DD> (brevo-engaged-v2-refresh)
```
then: v2 count before → after (+added / −removed) · list 7 count for comparison · overlap (both / list-7-only / v2-only) · the reasons histogram from the log · how much of the 11k pool the rotating slice has now covered · anything odd. Keep it factual.

**Decision watch (the point of this task):** once there are **4 consecutive weekly rows**, add a line to the log saying whether v2 has stabilised, and note that the audience switch is Joshua's call, not an automatic one. Do NOT change any campaign's recipient lists, do NOT edit list 7, and do NOT touch the `brevo-weekly-draft-guard` list spec — those stay as they are until Joshua says otherwise.

The task is complete only after this write returns.