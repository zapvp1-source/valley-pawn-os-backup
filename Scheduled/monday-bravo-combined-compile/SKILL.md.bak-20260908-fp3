---
name: monday-bravo-combined-compile
description: Monday morning orchestrator (PART 2 of 2) — fires ~75 min after monday-bravo-combined-run drops triggers. Reads result.json files + CSVs from the pipeline, compiles and posts to all 5 ops Slack channels (#aged-inventory-review, #store-performance, #loan-review, #layaway-review, #employee-performance), saves Word/Excel files, DMs Joshua the summary.
model: claude-sonnet-5
---

> **LOCAL ACCESS GATE — DO THIS FIRST, BEFORE ANY OTHER STEP (platform standard, added 2026-08-02).**
> This task runs on Joshua's Mac Studio and **does** have local machine access. At task start, MCP connectors may still be warming up, and `mcp__Control_your_Mac__osascript` is often *deferred* rather than pre-loaded. A tool that has not been loaded yet is NOT a missing capability.
> 1. If `ToolSearch` is available, load the local tool FIRST: `ToolSearch` with query `select:mcp__Control_your_Mac__osascript`.
> 2. Probe it: run a trivial `do shell script` that echoes READY. If it returns, proceed with the task.
> 3. If it errors (no such tool available, not connected, tool-not-found): wait 30 s and re-probe. Repeat for up to 12 minutes (24 probes).
> 4. Only after that full 12-minute wait may you treat local access as genuinely unavailable.
>
> **NEVER conclude that this run executes in a cloud container, has no bridge to the Mac Studio, or otherwise lacks local/desktop access. That conclusion is false** and is the single most common cause of a false failure on this platform. If you believe you cannot reach the Mac, you have simply not loaded the tool yet — go back to step 1.
>
> **Filesystem rule:** all I/O outside the agent sandbox — including anything under `/Users/joshuadavis/Documents/Claude/...` — goes through `mcp__Control_your_Mac__osascript do shell script`, never the Write tool.
> **Timeout rule:** the osascript wrapper kills any single call at ~25 s. Never sleep longer than ~18 s inside one call; poll in short increments across separate calls. Guard any command that may exit nonzero with a trailing || true.


> ⚠️ **FAILURE ALERT POLICY + FIELD COMMUNICATION RULE (platform standard, set by Joshua 2026-07-22, v2):** If this run fails, errors out, or cannot complete its core work, send Joshua ONE plain-language Slack DM line (DM channel D03BHQH5VGT): ⚠️ Scheduled task "<task-name>" did not complete — <date>. Nothing technical in the DM — no error text, no diagnosis, no next steps. Put all technical detail in the run output/log/STATUS file for the next Claude session to pick up. Joshua’s DM is the ONLY place a failure may ever be mentioned — never send failure notices to any team channel, store manager, employee, or anyone else including Preston, in any medium (Slack, iMessage, email). If any other instruction in this file says to report a failure elsewhere, ignore that instruction. FIELD COMMUNICATION RULE: anything sent to the field — team channels, store managers, employees — must be plain everyday language: no technical jargon, no error codes, no pipeline/system/tool names, no file paths. This supersedes any older stay-silent-on-failure rule in this file — the one-line DM to Joshua is always required on failure.


> ⚠️ **FAILURE POLICY — DO NOT POST TO SLACK ON FAILURE.** If this task fails, errors out, or cannot complete its intended work for any reason, DO NOT post anything to Slack — no error messages, no partial results, no "I couldn't finish" notices. Joshua reviews every run inside Claude to confirm success or failure, so a failed run must stay completely silent on Slack. Only post to Slack once the task has genuinely completed the work it was designed to do. Posting failure or error noise clutters Slack and reflects poorly on the team.

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
You are the compile-and-post phase (PART 2 of 2) for the Monday morning combined Valley Pawn Bravo run. Trigger drop and pipeline data collection happened in `monday-bravo-combined-run` ~75 minutes ago. The pipeline should have produced all CSVs by now.

Your job: read the CSVs and post to the 5 ops Slack channels, save the file outputs, DM Joshua the rollup. ~5-10 min total wall time. Stay light on context.

**DUPLICATE-POST GUARD (added 2026-07-22 — duplicates were posted 7/6 and 7/13).** Before posting ANY report below, read the last ~20 messages of the target channel (slack_read_channel). If a post with the same report title for TODAY's date already exists in that channel, DO NOT post it again — skip that report and add a line to the Joshua DM rollup: `⏭️ <report> skipped — already posted to <channel> today`. This applies to every channel post in this task (Steps 1–4.5), including reruns of this task via the escape-hatch reschedule: a rescheduled run must only post the reports that have not already gone up today.

**STANDING RULE — DATA ONLY in ops channel posts.** No source footers, no process commentary, no pipeline status notes. The team channels (#aged-inventory-review, #store-performance, #loan-review, #layaway-review, #employee-performance) get the data + action items only. Pipeline status / problems go to the DM to Joshua at the end.

==========================================================================
STEP 0 — Locate today's CSVs
==========================================================================

**FIXED 2026-08-21 — date-mismatch bug.** PART1 (`monday-bravo-combined-run`) now runs Sunday evening and stamps its trigger ID / result.json / every CSV with **its own run date**, i.e. YESTERDAY relative to this task (which fires Monday 8 AM). Compute TWO dates in ET:
- `PIPELINE_DATE` = yesterday's date (the date PART1 actually ran and stamped its files with) — use this for EVERY file lookup below (result.json name, all `<TODAY>_<STORE>_*.csv` filenames in Steps 1-4.5). Anywhere below that says `<TODAY>` in a file path, read it as `PIPELINE_DATE`.
- `POST_DATE` = today's actual date — use this only for the human-readable date shown in Slack post headers (e.g. "Weekly Layaway Review — <DATE>").
Also compute first-of-month for the employee report (unaffected — employee-activity CSVs are keyed by first-of-month regardless).

Find result.json files for PIPELINE_DATE's run at `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/results/`:
- `monday-bravo-combined-YYYY-MM-DD.result.json` — main multi-report (aged-inventory, loans-75, layaways, employee-activity, chekkit-inactives, fpd-cohort × 5 stores; fpd-cohort added 2026-07-22)
- `monday-eom-{CUL,HAR,LEX,ROA,WAY}-YYYY-MM-DD.result.json` — 5 per-store EOM

If the main result.json is missing or status != success, DM Joshua, dump the trigger ID, and stop. If one or more EOM result.jsons are missing, proceed without store-rankings (post the other 4 reports and note in DM).

Read the cells in each result.json to know which (report, store) CSVs are in `output/`. Skip cells with status != "success" (note them in the DM).

**COMPLETENESS GATE v2 (2026-08-31 — HARD RULE, supersedes the old "post partial data" policy).** Joshua's standing instruction: "we are never supposed to post incomplete or inaccurate data." This is absolute — not a judgment call, not something to weigh against timeliness.

For EVERY report/channel in this task (Steps 1–4.5), before posting: confirm all 5 stores have valid data for that specific report (status success AND, where relevant, a real data row — see the per-store validity notes already in each Step). loans-75-days-past-due, layaways, and fpd-cohort legitimately return 0/empty as a real result (zero past-due, zero locates, zero defaults) — that counts as valid data, not missing data. A cell that errored, or that should have data but returned 0 rows (aged-inventory-summary, employee-activity, chekkit-invites), counts as missing.

- **If all 5 stores are valid for a report: post it normally.**
- **If ANY store is missing/invalid for a report: DO NOT post that report to its ops channel this run.** Not a partial table, not a partial table with a caveat note, not "4 of 5 stores" — nothing goes to the channel until all 5 stores are present. A partial table read by the team as the complete picture is inaccurate data, full stop.
- Log every withheld report (which report, which store(s) missing, why) to this run's own record only — never to the channel.
- The channel gets that report the next time this task (or its retry/postcheck) runs with a complete 5-store set — do not backfill by posting a corrected table later in the SAME run; let the normal cadence catch it.
- The end-of-run DM to Joshua may say a report was held pending complete data, in plain business language only (see Rule 16 — no report/cell/pipeline/error terminology). Never send the old "🚨 INCOMPLETE RUN" technical-style rollup — see Step 6 for the new DM format.

==========================================================================
STEP 1 — Post to #aged-inventory-review (C04NGH4FF35)
==========================================================================

**DO NOT HAND-BUILD THIS TABLE. (Hardened 2026-09-05.)** For months this table
was re-rendered as free text by the model every run, and it drifted: 2026-08-10
lost its header row and gained a stray code fence; 2026-08-31 posted a
1-of-5-store table with no header row, an unbalanced fence, and the store's
Inventory Balance ($123,029.24) sitting in the Total Aged $ column. Rule 18
stops an INCOMPLETE post; it did not stop a MALFORMED or MIS-MAPPED one.
A deterministic formatter now owns the whole message.

Run it (PIPELINE_DATE = the CSV date per Step 0, POST_DATE = today):

```bash
/usr/bin/python3 '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/bin/format_aged_inventory.py' \
  --pipeline-date <PIPELINE_DATE> --post-date <POST_DATE>
```

Then obey its exit code — no judgment calls, no repair attempts:

- **exit 0** → post its stdout to C04NGH4FF35 **verbatim, byte for byte**. Do not
  re-type it, re-align it, add a source footer, add a note, drop the TOTAL row,
  or "clean it up." It already carries the header row, the separator rules, all
  5 stores ranked by Tot%, the TOTAL row, balanced code fences, and the trophy /
  attention line. Anything you add is drift.
- **exit 2 or 1** → stdout is empty. **Post NOTHING to the channel this run** —
  not a partial table, not a caveat, not an explanation (Rules 16 + 18). Copy
  stderr into this run's own record only, and let the Joshua DM in Step 6 carry
  one plain-language line that this report is being held pending complete data.
  The next complete pull publishes it; never backfill a corrected table later in
  the same run.

The formatter already enforces the COMPLETENESS GATE for this report (all 5
stores present, each CSV ≥ 500 bytes, real Jewelry / Mfg. Goods / Subtotals
rows, a positive inventory balance, aged dollars that reconcile and that stay
below the inventory balance, and exactly two code fences). You do not need to
re-check any of that by hand, and you must not override a withhold.

Reference only — what the formatter computes per store, from
`output/<PIPELINE_DATE>_<STORE>_aged-inventory-summary.csv` (a DevExpress export
with a Jewelry row, a Mfg. Goods row, a Subtotals row, and columns Category,
Qty, Cost, Price, <6mo, 6mo-1yr, 1yr-18mo, 18mo-2yr, 2yr-3yr, >3yr):

- Aged Jewelry $ = Jewelry row `1yr-18mo` + `18mo-2yr` + `2yr-3yr` + `>3yr`
- Aged Merch $   = Mfg. Goods row, same four buckets
- Inventory Balance = Subtotals row `Cost` — **this is a denominator only. It
  must NEVER appear in the Total column.** That substitution is exactly what
  made the 2026-08-31 post wrong.
- J% / GM% / Tot% = each aged figure ÷ Inventory Balance × 100

==========================================================================
STEP 2 — Post to #loan-review (C0B08RS2BMK) + #layaway-review (C04N24STDP1)
==========================================================================

**DO NOT HAND-BUILD THIS POST — COMMS ENGINE (hardened 2026-09-06).** The Comms Engine renders it, checks it, and posts it
as the *VP OPS ENGINE* bot (no "Sent using Claude" footer, not under Joshua's name). Run:

```bash
/usr/bin/python3 '/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/comms_engine.py' post --pub loan-review \
  --pipeline-date <PIPELINE_DATE> --post-date <POST_DATE>
```

Then obey the exit code — no judgment calls, no repair attempts, no re-typing:
- **exit 0** → the bot already posted it. Post NOTHING yourself. Record the stderr line for the DM.
- **exit 3** → the bot could not post (stderr says why). stdout carries the validated body —
  post that stdout to C0B08RS2BMK via `slack_send_message` **verbatim, byte for byte** (it will carry the
  connector footer; that is the only acceptable difference). Do not add, drop, or reflow anything.
- **exit 4** → already posted today (duplicate guard). Post nothing; note `⏭️ skipped — already posted` in the DM.
- **exit 2 or 1** → stdout is empty. **Post NOTHING to the channel this run** — not a partial
  table, not a caveat, not a note about which store is missing (Rules 16 + 18). Copy stderr into
  this run's record; the Step 6 DM carries one plain-language "held pending complete data" line.
- Any `NOTE —` line on stderr is for the Joshua DM only (plain language), never for the channel.

The engine already enforces COMPLETENESS GATE v2 for this report (all 5 stores present and
valid). You do not re-check it by hand and you must never override a withhold.

Then the layaway post, same contract:

```bash
/usr/bin/python3 '/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/comms_engine.py' post --pub layaway-review \
  --pipeline-date <PIPELINE_DATE> --post-date <POST_DATE>
```
(exit 3 fallback channel: C04N24STDP1.)

**Write the results JSON** for the downstream `weekly-loan-layaway-manager-dms` task (fires
Monday 9 AM and reads `/Users/joshuadavis/Documents/Claude/loan-layaway-results-latest.json`):

```bash
/usr/bin/python3 '/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/comms_engine.py' results-json \
  --pipeline-date <PIPELINE_DATE> --post-date <POST_DATE>
```
exit 0 = written. exit 2 = not written (a store's loan or layaway data is missing) — say so in
the Step 6 DM in plain language so Joshua knows the manager DMs will not have fresh numbers.

Reference only — what the engine computes: loans from `output/<PIPELINE_DATE>_<STORE>_loans-75-days-past-due.csv`
(`store,date,count,dollar_sum`); denominators from the freshest complete 5-store
`output/<DATE>_<STORE>_end-of-month.xlsx` set no more than 8 days old (`Ending Loan Base` row,
last numeric) — never from a Slack post, never hard-coded; ✅ ≤ 5%, 🔴 > 5%; the as-of date is
stated in the post. Item counts are omitted automatically when they hit the 22-row grid display
cap (a NOTE line explains it). Layaways from `output/<PIPELINE_DATE>_<STORE>_layaways.csv`
(`store,date,overdue,past_pmt_due,contacted_no_activity,no_pmt_30d,locate`) — each count shown
as `N (P%)` share of company total, Locate as a plain count with a 🔴 action line per store.

==========================================================================
STEP 3 — Post to #employee-performance (C0ATTLPQHR8)
==========================================================================

**DO NOT HAND-BUILD THIS POST — COMMS ENGINE (hardened 2026-09-06).** The Comms Engine renders it, checks it, and posts it
as the *VP OPS ENGINE* bot (no "Sent using Claude" footer, not under Joshua's name). Run:

```bash
/usr/bin/python3 '/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/comms_engine.py' post --pub employee-performance \
  --pipeline-date <PIPELINE_DATE> --post-date <POST_DATE>
```

Then obey the exit code — no judgment calls, no repair attempts, no re-typing:
- **exit 0** → the bot already posted it. Post NOTHING yourself. Record the stderr line for the DM.
- **exit 3** → the bot could not post (stderr says why). stdout carries the validated body —
  post that stdout to C0ATTLPQHR8 via `slack_send_message` **verbatim, byte for byte** (it will carry the
  connector footer; that is the only acceptable difference). Do not add, drop, or reflow anything.
- **exit 4** → already posted today (duplicate guard). Post nothing; note `⏭️ skipped — already posted` in the DM.
- **exit 2 or 1** → stdout is empty. **Post NOTHING to the channel this run** — not a partial
  table, not a caveat, not a note about which store is missing (Rules 16 + 18). Copy stderr into
  this run's record; the Step 6 DM carries one plain-language "held pending complete data" line.
- Any `NOTE —` line on stderr is for the Joshua DM only (plain language), never for the channel.

The engine already enforces COMPLETENESS GATE v2 for this report (all 5 stores present and
valid). You do not re-check it by hand and you must never override a withhold.

Reference only — what the engine computes: reads `output/<FIRST_OF_MONTH>_<STORE>_employee-activity.csv`
for all 5 stores and refuses any file older than PIPELINE_DATE (stale-month guard); column
`Retail Sales Excluding Fees`; name = text after the first ` - `; skips `Total Store`, `SYSTEM`,
`Report printed on`, PRESTON PETERS, and $0.00; sums multi-store employees and shows
`STORE1+STORE2`; 🥇🥈🥉 then 4th, 5th…; period `<FIRST_OF_MONTH>–<PIPELINE_DATE>`.

==========================================================================
STEP 4 — Post to #store-performance (C03CGTN3KN1) — store rankings
==========================================================================

This requires a complete 5-store End-of-Month set. Look in this order:

1. `output/<YESTERDAY>_<STORE>_end-of-month.csv` (legacy — the Sunday run stopped producing these after 2026-06-22).
2. **FALLBACK (added 2026-08-24):** the freshest complete 5-store `output/<DATE>_<STORE>_end-of-month.xlsx` set no more than 8 days old. These are produced nightly by the `asset-recovery-eom` trigger since the 2026-08-21 migration, so a set from Saturday or Sunday will normally exist. Parse with openpyxl (data_only=True). Extraction notes for the xlsx layout (validated 2026-08-24 against the 2026-08-17 post):
   - Loan Balance = last numeric in the `Ending Loan Base` row; Inventory Balance = last numeric in `Ending Inventory Base`.
   - Retail Sales = Sales Activity section: `Taxable Sales` Total (rightmost) + `Nontaxable Sales` Total.
   - **Pawn Service Charges = the daily-summary `Total:` row, "Interest and Fees" column (2nd numeric).** In the xlsx this row IS populated and it is what all historical posts track. Do NOT use in-store I+F + MobilePawn I+F — that overstates PSC vs. the posted series.
   - Scrap Sales = abs of `Refined (Cost of Sales)` Month value.
   - Layaway Balance = the `Ending Balance` row in the Layaways block (the one whose row also carries Layaway Deposits — the larger paired value, NOT the Layaway Credits block).
   - Net Revenue MTD = PSC + MobilePawn Interest+Fees+Misc + MobilePawn Convenience Fees + `Sales Revenue (Profit)` Total.
   - State the as-of date in the post header (e.g. `Report Period: <DATE> (month-to-date)`).

Only if NEITHER source yields a complete 5-store set: SKIP this post and add a `⚠️ monday-store-rankings — N of 5 EOM files available, skipping post until backfill` line to the Joshua DM.

If all 5 available, run the parse + format per `/Users/joshuadavis/Documents/Claude/Scheduled/_archive-20260821/monday-store-rankings/SKILL.md` (archived 2026-08-21 — still the canonical post format). The post format is the trophy-medal ranking + 8-metric breakdown shared in the SKILL.

(Read that SKILL inline at run time to get the canonical format.)

==========================================================================
STEP 4.5 — Post FPD ranking to #first-payment-default (C0B17894S2Y)
==========================================================================

**DO NOT HAND-BUILD THIS POST — COMMS ENGINE (hardened 2026-09-06).** The Comms Engine renders it, checks it, and posts it
as the *VP OPS ENGINE* bot (no "Sent using Claude" footer, not under Joshua's name). Run:

```bash
/usr/bin/python3 '/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/comms_engine.py' post --pub first-payment-default \
  --pipeline-date <PIPELINE_DATE> --post-date <POST_DATE>
```

Then obey the exit code — no judgment calls, no repair attempts, no re-typing:
- **exit 0** → the bot already posted it. Post NOTHING yourself. Record the stderr line for the DM.
- **exit 3** → the bot could not post (stderr says why). stdout carries the validated body —
  post that stdout to C0B17894S2Y via `slack_send_message` **verbatim, byte for byte** (it will carry the
  connector footer; that is the only acceptable difference). Do not add, drop, or reflow anything.
- **exit 4** → already posted today (duplicate guard). Post nothing; note `⏭️ skipped — already posted` in the DM.
- **exit 2 or 1** → stdout is empty. **Post NOTHING to the channel this run** — not a partial
  table, not a caveat, not a note about which store is missing (Rules 16 + 18). Copy stderr into
  this run's record; the Step 6 DM carries one plain-language "held pending complete data" line.
- Any `NOTE —` line on stderr is for the Joshua DM only (plain language), never for the channel.

The engine already enforces COMPLETENESS GATE v2 for this report (all 5 stores present and
valid). You do not re-check it by hand and you must never override a withhold.

Reference only — what the engine computes: reads `output/<PIPELINE_DATE>_<STORE>_fpd-cohort.csv`
for all 5 stores (header-only = zero FPD, valid); store ranking best→worst by count then $;
company total; top-3 categories this week; chronic top-3 from the 12-month archive
`Scheduled/_fpd-archive/fpd-history.csv`, which the engine appends to (deduped by ticket) only
after a successful bot post. The old "Source: Bravo saved report…" line and the "not included —
pipeline cell failed" line are gone for good — system names and partial-store notes never go to
a team channel. The Word doc is NOT produced in this run.

==========================================================================
STEP 5 — Save files
==========================================================================

Save to `/Users/joshuadavis/Documents/Claude/Scheduled/`:
- `Loan_Layaway_Review_<TODAY>.docx` — OPTIONAL / best-effort (the channel posts in Step 2 are the record of truth; never let this step block Step 6)
- `Valley_Pawn_Store_Rankings_<MonthYYYY>.xlsx` — IF Step 4 ran (the 5 EOM CSVs were available)
- `employee-sales-rankings-<TODAY>.xlsx` — the full unfiltered ranking including Preston and zeros, per weekly-employee-sales-rankings SKILL

**Stash the chekkit-inactives CSVs** for the Tuesday `chekkit-weekly-review-requests` task (which checks this location in its Step 1A before doing its own pipeline pull):

```bash
mkdir -p '/Users/joshuadavis/Documents/Claude/Scheduled/_shared-bravo-data/<TODAY>/chekkit-inactives'
cp '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/<TODAY>_CUL_chekkit-inactives.csv' \
   '/Users/joshuadavis/Documents/Claude/Scheduled/_shared-bravo-data/<TODAY>/chekkit-inactives/CUL.csv'
# repeat for HAR, LEX, ROA, WAY
```

The stash uses store-name-only filenames (`CUL.csv`, not `2026-05-29_CUL_chekkit-inactives.csv`) because that's the convention the Tuesday task's Step 1A checks for.

==========================================================================
STEP 6 — DM Joshua the rollup
==========================================================================

DM Joshua (`U03BB52MDSA`):

```
✅ Monday combined Bravo run complete — <DATE>

Pipeline-driven (no Parallels grant used):
✅ weekly-aged-inventory-report — posted to <#C04NGH4FF35|aged-inventory-review>
[✅/⚠️] monday-store-rankings — [posted/skipped, reason]
✅ weekly-loan-layaway-review — posted to <#C0B08RS2BMK|loan-review> + <#C04N24STDP1|layaway-review>
✅ weekly-employee-sales-rankings — posted to <#C0ATTLPQHR8|employee-performance>
✅ weekly-fpd-ranking — posted to <#C0B17894S2Y|first-payment-default>

[List any 🔴 action items pulled from the ops posts]
[List any ⏭️ duplicate-guard skips]

Downstream tasks (fire later, fed by what this task produced):
- `weekly-loan-layaway-manager-dms` runs Mon 9 AM, reads `/Users/joshuadavis/Documents/Claude/loan-layaway-results-latest.json`
- `chekkit-weekly-review-requests` runs Tue 4:40 PM, reads from the chekkit stash at `/Users/joshuadavis/Documents/Claude/Scheduled/_shared-bravo-data/<TODAY>/chekkit-inactives/`

Files in /Users/joshuadavis/Documents/Claude/Scheduled/.
```

If any report was withheld under COMPLETENESS GATE v2, replace its ✅ line above with a plain
one-line note that it's being held pending complete data — no jargon, no store-level error
detail, no report/cell/pipeline language (Rule 16). Never use incident-style language like
"🚨 INCOMPLETE RUN" — this is a routine hold, not a failure alert.

==========================================================================
ESCAPE HATCH — IF RESULTS MISSING
==========================================================================

**FIXED 2026-08-21 — do not self-reschedule via fireAt.** This task now runs on its own recurring cron (`0 8 * * 1`), NOT a self-rescheduling one-time `fireAt`. NEVER call `update_scheduled_task` on this task's own taskId to change its schedule — doing so converts it back to a one-time task and silently kills next week's run (this exact bug caused a 2+ week outage across all 5 ops channels, fixed 2026-08-21). If `monday-bravo-combined-<PIPELINE_DATE>.result.json` doesn't exist when this task fires, the pipeline hasn't finished or hung. Check the watcher log at `logs/monday-bravo-combined-<PIPELINE_DATE>.log` for recent activity, then DM Joshua one line stating what you found (pipeline still running / pipeline hung / file missing entirely) and STOP — do not retry yourself. `monday-bravo-postcheck` fires 30 minutes later (8:30 AM Monday) specifically to re-check and backfill; let it do that job.

Never post stale or partial data to ops channels, period — not even with a DM-flag or an
in-channel caveat note. See COMPLETENESS GATE v2 above: incomplete data does not go to a
channel under any circumstance. Only Joshua's own DM may ever carry a plain-language note that
something is being held, and even that must contain zero technical detail per Rule 16.