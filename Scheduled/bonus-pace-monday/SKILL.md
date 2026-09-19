---
model: claude-sonnet-5
name: bonus-pace-monday
description: Mondays 9:35 AM. Reads the Monday combined Bravo pull (no new Bravo touch) and DMs Joshua a one-line-per-store month-to-date pace against each store's bonus target, plus where each store stands on reviews, email, gold and Facebook. Never posts to a team channel.
---

> ⚠️ **FAILURE POLICY v3 (2026-09-08) — OVERRIDES every failure/DM instruction below.** On any failure, stall, expired login, missing connector, or anything you cannot complete: do NOT DM Joshua and do NOT message anyone. Append ONE row to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md` — `| <YYYY-MM-DD HH:MM ET> | <task-name> | <one plain sentence: what did not happen> | <NEEDS_HUMAN: no — or yes, <the one thing only Joshua can do>> | OPEN |` — then stop. `fleet-guardian` recovers, dedupes, and sends Joshua at most one DM a day. Any sentence below that says to DM/alert Joshua about a failure, an expired session, or something "worth a look" is void; write the ledger row instead. Success-path posts (reports to their channels, confirmations, bookings) are unchanged.

Valley Pawn weekly bonus PACE check. Autonomous, non-interactive, read-only against already-exported data.

HARD RULES
- Output ONLY to Joshua's DM (D03BHQH5VGT) while `field_posting` is false in `/Users/joshuadavis/Documents/Claude/Projects/Bonus Program/bonus_rules.json`. Never post to #bonus-goals or any team channel, never DM a manager or employee.
- Type B: never drop a Bravo trigger, never open Parallels, never use computer-use. Read only files the Monday combined run already produced. If today's files are not there yet, use the most recent ones and say plainly how current they are.
- Host access via mcp__Control_your_Mac__osascript `do shell script`.
- Rule 18: if fewer than 5 stores have usable data, say so plainly in the DM and give only the stores you actually have. Never estimate a missing store.

STEPS
1. MONTH = the current calendar month. Targets: `Bonus Program/data/<MONTH>/targets.json` (seeded on the 1st). If missing, take them from the latest #bonus-goals targets post and say which source you used.
2. Month-to-date net revenue per store: newest `Bravo Data Extraction/output/<date>_<STORE>_end-of-month.xlsx` whose Reporting Dates read "<M>/1/<YYYY> - ..." for the current month — Net Revenue = in-store Interest + Fees + Misc (In-Store Subtotal row) + Sales Revenue (Profit). Skip any file whose Reporting Dates span more than the current month; those are trailing-12-month pulls under a month filename.
3. Elapsed pace = days elapsed / days in month. For each store: MTD revenue, % of target, and whether they are ahead or behind straight-line pace.
4. Qualifier standing so far this month, where the data exists without a new pull: gold from `output/<year>_<STORE>_scrap-refining-gold.csv` (CLOSED buckets whose StatusDate falls in this month), email % from the newest `<date>_<STORE>_chekkit-invites-range.csv` for this month, reviews from the #google-reviews weekly posts this month. Leave anything you cannot source as a dash.
5. DM Joshua one compact code block: store, MTD revenue, target, % of target, ahead/behind, then the qualifier line. End with one plain sentence naming the store most at risk of missing and the store closest to a clean sweep. Plain language only — no jargon, no file paths.


## Final step (MANDATORY) — write the publication receipt

This task publishes to a surface with no readable history (a DM or a Slack canvas), so this receipt
is the ONLY evidence the task ran and delivered. Without it, a healthy run and a dead task are
indistinguishable in the fleet audit, and this task will read as AWAITING RECEIPTS forever.

Run this as the LAST action of the task, only after the publication actually succeeded:

```bash
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_receipt.py" write bonus-pace-monday \
  --surface slack-dm --target "D03BHQH5VGT" --note "<first line of what you published>"
```

Rules:
- Write it ONLY on a real, confirmed send. Never write a receipt for something you did not publish.
- If the task is silent by design this run (nothing to report), still write the receipt, with
  `--note "checked, nothing to report"`. Recording the look is what makes the silence trustworthy.
- If the publication FAILED, write it with `--ok false` and the reason in `--note`. Do not post the
  failure to Slack (Rule 16).


## Precondition (MANDATORY) — FLEET PUBLISH GUARD

Before publishing ANYTHING — a channel post, a DM to Joshua, a DM to a store manager, a canvas
refresh, an email, a Facebook post — check whether the fleet publish guard is armed:

```bash
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_dryrun.py" status
```

Exit code 0 means **ARMED**. When it is armed:

- Do the ENTIRE task for real — same pull, same data, same compile, same message text. The point is
  to test the task, not to skip it.
- Publish NOTHING. Not to a channel, not to a DM, not to a manager, not to a canvas, not anywhere.
- Instead write exactly what you would have published to
  `Valley Pawn OS/fleet/test_output/<task-name>-<YYYYMMDD-HHMMSS>.txt`, with a first line naming the
  channel or person it would have gone to.
- Do NOT write a normal publication receipt. A diverted run is not evidence that the task delivered,
  and recording it as one would corrupt the fleet audit.
- Say clearly in your final summary that the guard was armed and nothing was published.

Exit code 1 means not armed — run and publish normally.

This guard is ENFORCED for native scripts (they all publish through `vp_slack.py`, which intercepts
them). A Cowork task like this one has no such chokepoint, so here the guard is only as good as this
instruction. Honour it exactly. The guard always carries an expiry and disarms itself, so a stale
flag can never silence this task indefinitely.
