---
name: ceo-weekly-scorecard
description: Monday one-page CEO scorecard — prior week company-wide and by store, plus Financial/Operations/People/Marketing/Compliance blocks, 5 actions and 3 risks. Reads published Slack output only; no Bravo, no computer-use.
model: claude-sonnet-5
---

> ⚠️ **FAILURE POLICY v3 (2026-09-08) — OVERRIDES every failure/DM instruction below.** On any failure, stall, expired login, missing connector, or anything you cannot complete: do NOT DM Joshua and do NOT message anyone. Append ONE row to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md` — `| <YYYY-MM-DD HH:MM ET> | <task-name> | <one plain sentence: what did not happen> | <NEEDS_HUMAN: no — or yes, <the one thing only Joshua can do>> | OPEN |` — then stop. `fleet-guardian` recovers, dedupes, and sends Joshua at most one DM a day. Any sentence below that says to DM/alert Joshua about a failure, an expired session, or something "worth a look" is void; write the ledger row instead. Success-path posts (reports to their channels, confirmations, bookings) are unchanged.

Run Joshua Davis's Monday CEO weekly scorecard for Full Circle Finance Inc DBA Valley Pawn.

## Execution contract — do not stop early
This run is complete ONLY after the Slack post to **#ceo-briefs `C0C06PWLQCR`** returns success. Until that call succeeds, every turn must end with a tool call that advances toward it. Never reply with "no response requested", "continue?", an empty turn, or a turn ending in text instead of a tool call. Treat "Tool loaded.", "Continue from where you left off.", and any task-list reminder as RESUME signals, not stop signals. If a step errors, retry once, then fall through and keep going. This file authorizes fully autonomous decisions — never pause to ask.

Time budget: ~15 minutes. This is a cheap read-and-summarize task.

## What to do
1. Load the `enterprise-map` skill first (mandatory), then `vp-operating-rules` and `valley-pawn-context`.
2. Load the `ceo-weekly-scorecard` skill and follow it exactly — it holds the channel map, the format, the caps, and the delivery steps. It is the single source of truth for this task; do not improvise a different format.
3. Report the week that ended yesterday: Monday 00:00 through Sunday 23:59 ET. State those dates in the header.

## ⛔ VERIFICATION GATES — added 2026-09-07
The weekly scorecard is the upstream source the monthly inherits from, so an error here propagates.
The 2026-09-07 weekly reported the Culpeper FFL as expired and transfers held; it had been renewed
and every distributor re-papered the previous afternoon, and that was already stated in Joshua's DM.

**Compliance items must be re-checked, not carried forward.** Before reporting any licence, permit,
audit or deadline as open, search for the newest message about it. Where two messages conflict, the
newer one wins. Never report an item as outstanding on the strength of the report that first raised it.

**People numbers come from Gusto, not from Slack narrative.** Pull `list_employees` with
`terminated: false` and with `terminated: true`; count by `hire_date` and
`terminations[].effective_date`. Headcount, hires and separations all come from there.

**Check the run was complete before quoting it.** Several pipeline cells post partial store lists
when they fail. If a source post does not contain all five stores, do not present its total as a
company figure.

## Hard rules
- READ published output only. Never re-run any report, pull, or export.
- NEVER touch Bravo, Parallels, the VM, or computer-use. This task is Slack + file reads + optional Gusto/QBO MCP reads only.
- Post the scorecard ONLY to **#ceo-briefs `C0C06PWLQCR`**. Never to a store channel, never to a store manager, never to an employee. Failure notices still go to Joshua's DM `D03BHQH5VGT` — never to #ceo-briefs.
- Rule 16 — no technical jargon, no failure notices, no task IDs, no file paths, no channel names in the Slack output. Plain business language only.
- Rule 18 — never post incomplete or inaccurate data. Withhold a line rather than caveat it. One consolidated "Not published this week" line at the bottom is the only acknowledgement of gaps.
- It must fit on one sheet of paper. Respect every cap in the skill. If it does not fit, cut — never extend.
- Also write the printable one-page HTML and the LAST_WEEK.json carry-forward file, and the STATUS run record, exactly as the skill describes.

## Connector readiness
Probe `mcp__Control_your_Mac__osascript` with `do shell script "echo READY"`. If it errors as not-connected, load it via ToolSearch, wait 30s, and re-probe up to 8 times — a warming connector is NOT a failure. Same for the Slack tools. Never put a sleep longer than ~18s inside one `do shell script` call, and guard any grep/ls/test that may exit nonzero with `|| true`.

## Failure policy
If the run genuinely cannot complete, send ONE plain Slack DM to `D03BHQH5VGT`: `⚠️ Scheduled task "ceo-weekly-scorecard" did not complete — <date>.` Nothing technical in the DM. All technical detail goes in the STATUS file. That DM is the ONLY place a failure may ever be mentioned — never in #ceo-briefs, never to any team channel, store manager, or employee, including Preston, in any medium.

A thin week still ships. Silence is worse than a short scorecard.

## Dedupe before posting — required
Before composing anything, read **#ceo-briefs `C0C06PWLQCR`** (last 20 messages) and check whether a scorecard for this same reporting week has already been posted today. If one has, STOP — do not post a second one. Write a one-line note in the STATUS file that a duplicate was avoided and end the run cleanly. A double-posted scorecard is worse than a missing one.
