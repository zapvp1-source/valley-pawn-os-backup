---
name: yield-by-asset-class-monthly
description: Day 6, 2:00 PM. Mostly file reads; ONE Type A trigger drop for the Company KPI channel split (no computer-use, no direct screen drive). Recomputes Valley Pawn loan/inventory/blended yield from End-of-Month exports, runs a 6-check regression harness, and republishes the Yield by Asset Class artifact. Withholds everything if any check fails.
model: claude-sonnet-5
---

> ⚠️ **FAILURE POLICY v3 (2026-09-08) — OVERRIDES every failure/DM instruction below.** On any failure, stall, expired login, missing connector, or anything you cannot complete: do NOT DM Joshua and do NOT message anyone. Append ONE row to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md` — `| <YYYY-MM-DD HH:MM ET> | <task-name> | <one plain sentence: what did not happen> | <NEEDS_HUMAN: no — or yes, <the one thing only Joshua can do>> | OPEN |` — then stop. `fleet-guardian` recovers, dedupes, and sends Joshua at most one DM a day. Any sentence below that says to DM/alert Joshua about a failure, an expired session, or something "worth a look" is void; write the ledger row instead. Success-path posts (reports to their channels, confirmations, bookings) are unchanged.

Refresh Valley Pawn's Yield by Asset Class report for Full Circle Finance Inc.

## What this is
Monthly yield on deployed capital, split into its two asset classes:
- **Loan Yield** = pawn service charges (in-store Interest + Fees + Misc) ÷ prior-month Ending Loan Base
- **Inventory Yield** = Sales Revenue (Profit) ÷ prior-month Ending Inventory Base
- **Blended** = Net Revenue ÷ prior-month (Loan Base + Inventory Base) — this is the SAME "Yield" the bonus program uses; it is not being redefined here.

Layaway is deliberately NOT a third asset class — its gross profit is already inside Sales Revenue (Profit) and its merchandise already inside the Inventory Base, so a separate layaway yield double-counts. Report it only as a collection-velocity sub-metric. Full reasoning: `Bravo Data Extraction/YIELD_BY_ASSET_CLASS.md`. Do not "improve" on this.

## TYPE B — no Bravo contact
This task reads files already on disk. It must NEVER drop a pipeline trigger, run the health gate, launch Parallels, or use computer-use. No contention check is needed because nothing touches Bravo's screen. If a month's data is missing, that is a finding to report — not a reason to pull anything.

## Steps

**0. Refresh the channel split (this is the ONE Bravo touch, and it is a trigger drop).**
The End-of-Month export gives a single combined inventory gross-profit figure. Only Bravo's
**Company KPI** report splits retail gross profit from scrap gross profit, which is what makes the
"is non-gold growing?" question answerable. Drop ONE trigger covering the current year to date and
the same window last year:

```
do shell script "cat > '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/triggers/yield-channel-<YYYYMMDD>.json' << 'EOF'
{"id":"yield-channel-<YYYYMMDD>","requested_at":"<ISO>","reports":[{"name":"company-kpis","stores":["ALL"],"date":"<PRIOR_YEAR>-01-01..<PRIOR_YEAR>-<MM>-<LASTDAY>"},{"name":"company-kpis","stores":["ALL"],"date":"<THIS_YEAR>-01-01..<THIS_YEAR>-<MM>-<LASTDAY>"}]}
EOF"
```
where `<MM>-<LASTDAY>` is the last completed month. This is a **Type A** trigger drop — the watcher
serialises it, so no foreground guard is needed, but do run the contention check first
(`bash '.../Bravo Data Extraction/_bravo_foreground_guard.sh' check`) and if it returns BUSY, skip
this step and carry on with the existing channel data rather than waiting.

Poll `output/` for the two `<END_DATE>_ALL_company-kpis.xlsx` files (each takes 1-3 minutes; poll in
short increments, never sleep more than ~18s in one osascript call). When they land — or after ~12
minutes, whichever first — run:
```
do shell script "cd '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction' && /usr/bin/python3 channel_growth.py 2>&1"
```
If the pulls did not arrive, continue anyway. `render_yield_artifact.py` simply omits the channel
section when `output/channel_growth.json` is absent or stale rather than showing invented figures.

**GOTCHA:** company-kpis output is named by END DATE only, same trap as the End-of-Month export
(see `eom_validate.py`). Never pull two different ranges that share an end date in one cycle.

**1. Run the regression harness. This is a hard gate.**
```
do shell script "cd '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction' && /usr/bin/python3 test_yield_by_asset_class.py 2>&1"
```
It regenerates the data and asserts six things: the Preston June-2026 penny match, the bonus-engine August-2026 cross-check, the sales-component identity that underpins the layaway call, that every published month resolves to a true full-month file, that the loan/inventory split reconciles to blended on every row, and that all five stores plus COMPANY are present. Takes ~90 seconds.

- **Exit 0 / "RESULT: PASS"** → continue to step 2.
- **Exit 1 / "RESULT: FAIL"** → STOP. Publish nothing, post nothing, do not republish the artifact. Append the full harness output to `Bravo Data Extraction/YIELD_RUN_LOG.md` with today's date, then send Joshua ONE plain-language Slack DM (channel D03BHQH5VGT) and nothing else: `⚠️ Scheduled task "yield-by-asset-class-monthly" did not complete — <date>.` No error text, no diagnosis, no next steps in the DM. Then end the run.

**2. Regenerate the artifact's data.**
```
do shell script "cd '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction' && /usr/bin/python3 render_yield_artifact.py '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/artifact/yield-by-asset-class.html' 2>&1"
```
Every figure on the page — headline tiles, tables, chart, and the narrative sentences — is computed from the embedded data blob this script rewrites. Nothing on that page is hand-typed, so do NOT hand-edit numbers into the HTML. If the script reports it could not find exactly one data block, stop and follow the failure path in step 1.

**3. Republish the artifact to the SAME url (this keeps the link Joshua already has).**
Use the Artifact tool with `url: https://claude.ai/code/artifact/a2c1c285-29a3-4c6c-9388-f9b460063239` and the file path from step 2. Read it first (`action: "read"` with that url) as the tool requires before publishing to an artifact this conversation has not published. Give the version a short label like `<Month> <Year> refresh`. Do NOT pass a favicon — the artifact keeps the one it has.

**4. Append a run entry** to `Bravo Data Extraction/YIELD_RUN_LOG.md`: date, months covered, company loan/inventory/blended for the latest month and year-to-date, which sources the resolver used (the extractor prints this), and anything notable.

**5. DM Joshua** (Slack channel D03BHQH5VGT) — one short, plain message, no jargon, no file paths, no tool or pipeline names:
> Yield update through <Month>. Company blended <X>% a month (<Y>% a year) — loans <A>%, inventory <B>%. <One sentence on what moved and which store stands out.> Full report updated at the usual link.

Take the figures from the CSV at `Bravo Data Extraction/output/yield_by_asset_class.csv` (COMPANY rows). Annualized = monthly × 12.

## Hard rules
- **Rule 18 — withhold, don't caveat.** Never publish a partial or uncertain figure. If fewer than 5 stores resolve for a month, that month is simply absent; never footnote a 4-store number as if it were the company.
- **Rule 16 — no failure notices anywhere but Joshua's DM.** Never post a failure, error, or technical detail to any team channel, manager, or employee, in any medium. Technical detail goes to YIELD_RUN_LOG.md only.
- **Rule 4 — additive only.** Do not modify `EndOfMonth.ahk`, `OutputFilename()`, `monthly-analytics-prestage`, `layaway-yield-weekly`, `store_kpis_compile.py`, `bonus_kpis_extract.py`, or any existing scheduled task or saved Bravo report. If a fix seems needed in one of those, log it in `Life OS/OPEN_ITEMS_REGISTER.md` for Joshua instead.
- Post to no Slack channel other than Joshua's DM. This is an internal metric, not a field communication.

## Known context worth carrying
Bravo's EOM export is named by END DATE only, and the monthly analytics job pulls six different date windows per store that all end on the same day — so the canonical month file can be silently overwritten by a trailing-12-month or YTD pull. `eom_validate.py` handles this: it checks every file's own reporting-date header, falls back to the range-stamped staged copies and the `eom_archive/` folder, and refuses anything whose range is not exactly the month. This is why the harness's range check exists. If it ever fails, the fix is to look at what overwrote the file — never to relax the check.
