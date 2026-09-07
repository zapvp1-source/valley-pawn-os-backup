---
name: bonus-pace-monday
description: Mondays 9:35 AM. Reads the Monday combined Bravo pull (no new Bravo touch) and DMs Joshua a one-line-per-store month-to-date pace against each store's bonus target, plus where each store stands on reviews, email, gold and Facebook. Never posts to a team channel.
---

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