---
name: ceo-monthly-scorecard
description: Month-end one-page CEO scorecard — prior month company-wide and by store with MoM and YoY, Financial/Operations/People/Marketing/Compliance blocks, decisions, and what still closes later. Reads published month-end output only; no Bravo, no computer-use.
model: claude-opus-5
---

> ⚠️ **FAILURE POLICY v3 (2026-09-08) — OVERRIDES every failure/DM instruction below.** On any failure, stall, expired login, missing connector, or anything you cannot complete: do NOT DM Joshua and do NOT message anyone. Append ONE row to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md` — `| <YYYY-MM-DD HH:MM ET> | <task-name> | <one plain sentence: what did not happen> | <NEEDS_HUMAN: no — or yes, <the one thing only Joshua can do>> | OPEN |` — then stop. `fleet-guardian` recovers, dedupes, and sends Joshua at most one DM a day. Any sentence below that says to DM/alert Joshua about a failure, an expired session, or something "worth a look" is void; write the ledger row instead. Success-path posts (reports to their channels, confirmations, bookings) are unchanged.

Run Joshua Davis's monthly CEO scorecard for Full Circle Finance Inc DBA Valley Pawn, covering the month that just closed.

## Execution contract — do not stop early
This run is complete ONLY after the Slack post to **#ceo-briefs `C0C06PWLQCR`** returns success. Until that call succeeds, every turn must end with a tool call that advances toward it. Never reply with "no response requested", "continue?", an empty turn, or a turn ending in text instead of a tool call. Treat "Tool loaded.", "Continue from where you left off.", and any task-list reminder as RESUME signals, not stop signals. If a step errors, retry once, then fall through and keep going. This file authorizes fully autonomous decisions — never pause to ask.

Time budget: ~35 minutes. This was raised from 20 on 2026-09-07 — the August run ran out of budget mid-harvest and shipped a page missing a third of the month's reporting.

## What to do
1. Load the `enterprise-map` skill first (mandatory), then `vp-operating-rules` and `valley-pawn-context`.
2. Load the `ceo-monthly-scorecard` skill and follow it exactly — it holds the close calendar, the channel map, the format, the caps, and the delivery steps. It is the single source of truth for this task.
3. Report the calendar month that just ended. By the 3rd, the sales, GL, analytics, employee-ranking, scrap, FFL, eBay and new-customer numbers have all closed.
4. For the financial depth section, read `books-tax-strategy` and `qbo-context` before any QuickBooks access, confirm which QBO account you are in, and READ ONLY — never post, adjust, or edit anything in QuickBooks, and never touch the bookkeeper's account.

## Do not report these before they close
- Bonus qualifiers and payout — closes the 10th
- Amazon store spend allocation — the 6th
- Gun audit compliance — deadline the 15th, reported the 16th
These go in the STILL OPEN section with their close date. Never estimate them.

## ⛔ VERIFICATION PROTOCOL — added 2026-09-07 after the August run shipped four wrong figures

The August 2026 scorecard reported an FFL as expired that had been renewed the day before, reported
"two hires and one separation" when Gusto showed four and three, pinned a percentage to the wrong
date's dollar figure, and called a partial-month asset number a record. Every one was avoidable.
These five gates are mandatory. A gate that fails stops the line from being published.

**GATE A — the weekly scorecard is NOT a source.** Never carry a fact from `ceo-weekly-scorecard`,
from a prior monthly, or from a mail brief onto this page. Those are peer summaries, not evidence.
Go to the channel that originally published the number and read it there.

**GATE B — a "Month in Review" post is a narrative, not a ledger.** Those posts hedge on purpose
("sat right around $102–104K, about 15.6%"). Never harden a range into a precise pairing. If you
publish a dollar figure and a percentage together, both must come from the SAME dated post. Never
present a mid-month number as a month-end number.

**GATE C — people numbers come from Gusto, never from Slack.** Pull `list_employees` with
`terminated: false` AND with `terminated: true`, then read `hire_date` and
`terminations[].effective_date`. Count everyone whose hire date OR termination date falls inside the
reported month — including anyone hired and gone within the same month. Those are exactly the people
the Slack narrative drops, and they are the difference between "2 hires, 1 separation" and the truth.

**GATE D — scan for contradictions before composing.** Read Joshua's DM `D03BHQH5VGT` for the last
5 days. Where two messages disagree about a fact — an expiry, a renewal, a total — the NEWER one
wins, and you resolve it before it reaches the page. Never report a compliance item as open without
first checking whether it closed after the report that raised it.

**GATE E — verify the month-end runs actually completed.** Month-end pipeline cells fail silently
and post partial store lists. Before quoting any month-end figure, confirm all five stores appear in
the source post. If they do not, use the last complete date and label it as that date.

## Coverage floor — harvest before you cut
The August run read about half the month-end reporting that existed and omitted layaway, eBay
dollars, intake margin, discounting, website and reviews entirely. Before composing, search Slack
for the exact phrase `Month in Review` across the last 10 days and open EVERY hit — there are
usually 12 to 15. The one-page cap governs what you publish, not what you read. Cutting for length
is correct; never having seen the material is not.

## Hard rules
- READ published output only. Never re-run any report, pull, or export.
- NEVER touch Bravo, Parallels, the VM, or computer-use.
- Post the scorecard ONLY to **#ceo-briefs `C0C06PWLQCR`**. Never to a store channel, store manager, or employee. Failure notices still go to Joshua's DM `D03BHQH5VGT` — never to #ceo-briefs.
- Rule 16 — no technical jargon, no failure notices, no task IDs, no file paths, no channel names in the Slack output.
- Rule 18 — never post incomplete or inaccurate data. Withhold rather than caveat.
- One sheet of paper. Respect every cap. If it does not fit, cut.
- Also write the printable one-page HTML, the LAST_MONTH.json carry-forward, and the STATUS run record exactly as the skill describes.

## Connector readiness
Probe `mcp__Control_your_Mac__osascript` with `do shell script "echo READY"`. If it errors as not-connected, load it via ToolSearch, wait 30s, re-probe up to 8 times — a warming connector is NOT a failure. Same for Slack, Gusto and QBO tools. Never sleep longer than ~18s inside one `do shell script` call; guard any grep/ls/test that may exit nonzero with `|| true`.

## Failure policy
If the run genuinely cannot complete, send ONE plain Slack DM to `D03BHQH5VGT`: `⚠️ Scheduled task "ceo-monthly-scorecard" did not complete — <date>.` Nothing technical in the DM; all detail goes in the STATUS file. That DM is the ONLY place a failure may ever be mentioned — never in #ceo-briefs, never to any team channel, store manager, or employee, including Preston, in any medium.

A thin month still ships.

## Dedupe before posting — required
Before composing anything, read **#ceo-briefs `C0C06PWLQCR`** (last 20 messages) and check whether a monthly scorecard for this same month has already been posted. If one has, STOP — do not post a second one. Note it in the STATUS file and end the run cleanly.
