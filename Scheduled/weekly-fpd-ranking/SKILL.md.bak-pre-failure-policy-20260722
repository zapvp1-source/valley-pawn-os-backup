---
name: weekly-fpd-ranking
description: Weekly first-payment-default (FPD) ranking by Valley Pawn store, plus category/item risk breakdown, posted to #first-payment-default every Monday morning. Pipeline-driven via saved Bravo report "Claude First Payment Default" — no Parallels grant required. Standalone trigger drop; does NOT piggyback on monday-bravo-combined-run.
---

> ⚠️ **FAILURE POLICY — DO NOT POST TO SLACK ON FAILURE.** If this task fails, errors out, or cannot complete its intended work for any reason, DO NOT post anything to Slack — no error messages, no partial results, no "I couldn't finish" notices. Joshua reviews every run inside Claude to confirm success or failure, so a failed run must stay completely silent on Slack. Only post to Slack once the task has genuinely completed the work it was designed to do. Posting failure or error noise clutters Slack and reflects poorly on the team.

You are running Joshua Davis's weekly First-Payment-Default ranking + category/item risk analysis for Valley Pawn / Full Circle Finance Inc.

**The metric.** FPD = the set of loans originated 60–90 days ago for which the customer has never made any payment (no redeem, no renewal interest, no partial pay). The cohort window and the "no payment" filter are both encoded inside the Bravo saved report named **"Claude First Payment Default"**. The watcher runs that report per store and dumps **one CSV row per defaulted loan**, with the columns the report exposes (currently: `Ticket Number, Category, Full Description, Loan Amount`).

FPD is a leading indicator of underwriting / origination quality. A 30-day pawn loan that reaches 60–90 days past origination with zero customer activity is a clean signal that the loan should not have been written, the loan-to-value was too aggressive, or customer evaluation broke down.

**How this task works.** This task does NOT drive Bravo's UI. The Bravo Data Extraction pipeline runs inside a Windows VM and produces one row-level CSV per store on demand. This task drops one trigger file (via osascript since the pipeline folder is outside the agent's sandbox), waits for the CSVs, computes the rankings AND the category/item breakdowns, then posts to Slack and saves a Word doc.

**Standalone — do NOT modify `monday-bravo-combined-run`.** That orchestrator is working and is out of scope for this skill.

⚠️ **CRITICAL — DO NOT use the Write tool to drop the trigger file.** The Bravo Data Extraction folder (`/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/`) is OUTSIDE this task's sandbox. Use `mcp__Control_your_Mac__osascript` instead.

═══════════════════════════════════════════════
STEP 1 — Drop the Bravo trigger
═══════════════════════════════════════════════

**1a. Generate a trigger ID:**

```
weekly-fpd-ranking-YYYY-MM-DDTHH-MM-SS
```

**1b. Build the trigger JSON.** ONE report, all 5 stores, today's date:

```json
{
  "id": "weekly-fpd-ranking-2026-05-18T09-03-00",
  "requested_at": "2026-05-18T09:03:00-04:00",
  "reports": [
    {
      "name": "fpd-cohort",
      "stores": ["CUL", "HAR", "LEX", "ROA", "WAY"],
      "date": "2026-05-18"
    }
  ]
}
```

The cohort window and the "no payment" filter live inside the saved Bravo report — the trigger does NOT need date_from/date_to. The `date` field is just the run date used for the output CSV filename.

**1c. Write via osascript:**

```applescript
set triggerId to "weekly-fpd-ranking-2026-05-18T09-03-00"
set triggerJson to "{\"id\": \"" & triggerId & "\", \"requested_at\": \"2026-05-18T09:03:00-04:00\", \"reports\": [{\"name\": \"fpd-cohort\", \"stores\": [\"CUL\",\"HAR\",\"LEX\",\"ROA\",\"WAY\"], \"date\": \"2026-05-18\"}]}"
set triggerPath to "/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/triggers/" & triggerId & ".json"
do shell script "echo " & quoted form of triggerJson & " > " & quoted form of triggerPath
return "dropped " & triggerPath
```

═══════════════════════════════════════════════
STEP 2 — Poll for completion
═══════════════════════════════════════════════

The watcher polls `triggers/` every 30s. Walking the grid takes longer than the previous count-only flow — budget ~3–6 minutes per store, ~15–30 minutes for all 5. Poll every 30s via osascript:

```applescript
do shell script "test -f '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/results/" & triggerId & ".result.json' && echo READY || echo PENDING"
```

Loop with a 30s delay between polls. Time out at **40 minutes** (80 polls).

When `READY`, read the result JSON:

```applescript
do shell script "cat '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/results/" & triggerId & ".result.json'"
```

Parse the returned JSON. For each cell with `status="success"`, the `output_path` field points to that store's CSV. For any cell with `status != "success"`, treat that store as `❓ Could not compute` — continue with the stores that succeeded. If a store has `count_from_title=0`, the CSV will still exist with only the header row — that's a clean store (zero FPD), NOT a missing read.

If the timeout fires with no result JSON, DM Joshua at `U03BB52MDSA` with the trigger ID and the failure, then post a partial-data Slack notice and stop.

═══════════════════════════════════════════════
STEP 3 — Read each CSV (row-level)
═══════════════════════════════════════════════

For each successful cell, read its CSV via osascript:

```applescript
do shell script "cat '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/2026-05-18_CUL_fpd-cohort.csv'"
```

**CSV shape (header + ONE data row per defaulted loan):**

```
Ticket Number,Category,Full Description,Loan Amount
BT-VAP021107,Gold-Stone Bracelet,"3.4DWT 14K-Y/G, 5-ROUND CUT ABALONE 12.36CTW",$102.00
BT-VAP021125,Silver Chain,27.3DWT SILV-925,$30.00
...
```

Notes on parsing:
- The `Loan Amount` column is a string like `$102.00`. Strip `$` and `,` before float-parsing.
- `Full Description` may contain commas — the CSV is double-quoted where needed (standard Buys grid behavior). Parse with a real CSV parser, not naive split-on-comma.
- An empty CSV (header only) means zero FPD loans at that store — include it in the ranking with count 0 / $0.
- The `Category` column is the most useful aggregation key. Examples seen in practice: `Gold-Stone Bracelet`, `Silver Chain`, `Handgun`, `Power Tool`, `Television`, `Game Console`, etc.

For each row, derive:
- `store` from the filename (`2026-05-18_CUL_fpd-cohort.csv` → `CUL`)
- `loan_amount` (float)
- `category` (string)
- `full_description` (string)
- `ticket_number` (string)

Build three aggregations:

**A. Per-store totals** (for the existing ranking)
| Store | FPD Count | $ Exposure |

**B. Top default-prone CATEGORIES, company-wide.** Group all rows by `Category`, sum count and $. Rank descending by count, tie-break by $.

**C. Top default-prone CATEGORIES, per store.** Same grouping but filtered to each store.

**D. Largest individual defaulted LOANS, company-wide.** Top 10 by `Loan Amount` descending.

Compute company totals: `Σ count`, `Σ $ exposure`.

═══════════════════════════════════════════════
STEP 3.5 — Append to the 12-month FPD history archive
═══════════════════════════════════════════════

**Purpose.** Each weekly snapshot is a rolling 60–90-day window, so individual loans appear in multiple consecutive weeklies. The archive lets us answer "what categories and items chronically default" over a 12-month horizon — distinct from "what's bleeding this week."

**Archive file.** `/Users/joshuadavis/Documents/Claude/Scheduled/_fpd-archive/fpd-history.csv` — append-only, deduped by `Ticket Number`. Columns:

```
first_seen_date,store,ticket_number,category,full_description,loan_amount
```

**Append logic** (via osascript):

1. Create the archive folder if it doesn't exist.
2. If `fpd-history.csv` doesn't exist, write the header row first.
3. Load existing ticket numbers into a set.
4. For each row in today's per-store CSVs, if `ticket_number` is not in the set, append it with `first_seen_date = today` and the row's other fields.

This ensures every defaulted loan is captured exactly once across the rolling weekly snapshots.

**12-month rollups** (compute fresh each Monday from the archive):

- Filter rows where `first_seen_date >= today - 365 days`.
- **Top 3 categories (12-month)** by count, with $ exposure as tie-break.
- **Top 10 items (12-month)** — group by either (a) exact `Full Description`, or (b) `Category + first-3-words-of-description` to avoid serial-number-style variants splitting groups. Use (b) by default; show both Category and the canonical description.

═══════════════════════════════════════════════
STEP 4 — Rank and post to Slack
═══════════════════════════════════════════════

Sort store ranking ascending by `count` (lowest count = best underwriting at top). Ties on count break by `$ exposure` ascending. Any store with `❓ Could not compute` lists last with that note.

Post to `#first-payment-default` (`C0B17894S2Y`) via `slack_send_message`. Format:

```
🎯 *Weekly First-Payment-Default Ranking — [today]*
_Source: Bravo saved report "Claude First Payment Default" · cohort = loans originated 60–90 days ago with no customer payment activity_

*Store ranking — best to worst*
1. *[STORE]* — [N] FPD loans • $[exposure] exposure
2. *[STORE]* — [N] FPD loans • $[exposure] exposure
3. *[STORE]* — [N] FPD loans • $[exposure] exposure
4. *[STORE]* — [N] FPD loans • $[exposure] exposure
5. *[STORE]* — [N] FPD loans • $[exposure] exposure

*Company:* [ΣN] FPD loans • $[Σexposure] total exposure

*Top default-prone categories (this week)*
1. [CATEGORY] — [N] loans • $[exposure]
2. [CATEGORY] — [N] loans • $[exposure]
3. [CATEGORY] — [N] loans • $[exposure]

*Chronic-risk categories (last 12 months)*
1. [CATEGORY] — [N] total FPD loans • $[exposure]
2. [CATEGORY] — [N] total FPD loans • $[exposure]
3. [CATEGORY] — [N] total FPD loans • $[exposure]
```

**STANDING RULE — DATA ONLY.** Operations reads this channel. No pipeline status notes, no commentary. The title, the store ranking, the Company line, the two top-categories blocks — that's it. Pipeline status / partial-data commentary belongs in a DM to Joshua, not the ops channel.

If a store could not be computed, append exactly one line after the chronic block: `_Note: [STORE(S)] not included — pipeline cell failed._`

═══════════════════════════════════════════════
STEP 5 — Save the Word doc
═══════════════════════════════════════════════

Use the `docx` skill to generate `FPD_Ranking_[YYYY-MM-DD].docx` in the agent's outputs folder, then copy it to `/Users/joshuadavis/Documents/Claude/Scheduled/` via osascript so it persists:

```applescript
do shell script "cp '<agent outputs path>/FPD_Ranking_2026-05-18.docx' '/Users/joshuadavis/Documents/Claude/Scheduled/FPD_Ranking_2026-05-18.docx'"
```

The doc must contain:

1. **Title:** `Valley Pawn — First-Payment-Default Ranking — [today]`

2. **Methodology paragraph** — source = Bravo saved report "Claude First Payment Default"; cohort = loans originated 60–90 days ago with no payment activity; weekly snapshots deduped into a 12-month archive for chronic-risk analysis.

3. **Store ranking table** sorted ascending by count: Rank, Store, FPD Count, $ Exposure.

4. **This-week top default-prone categories — company-wide.** Table: Rank, Category, Count, $ Exposure, % of total count. Top 10 (or all if fewer).

5. **Per-store category breakdown.** For each store, list its top 3 categories this week (Category, Count, $ Exposure).

6. **Largest individual defaulted loans (this week).** Table of top 10 single tickets company-wide: Store, Ticket #, Category, Description, Loan Amount.

7. **12-month chronic-risk section** (uses `fpd-history.csv`):
   - **Top 3 categories (12-month)** table: Rank, Category, Total FPD loans, Total $ Exposure, # distinct stores hit, % of all 12-month FPDs.
   - **Top 10 chronic items (12-month)** table: Rank, Category, Canonical description, Count seen, Total $ Exposure, Stores it shows up in. Grouping = `Category + first-3-words-of-description` to avoid serial-number variants.
   - Companion note explaining the dedupe (each loan appears once even though it shows up in multiple weekly snapshots).

8. **Trend section** — only if last week's doc exists. For each store, show this-week count vs. last-week count and the delta (+/- N). Also show company-wide count delta and total-$-exposure delta.

9. **Stores to watch** — any store whose count exceeds the company average (`ΣN / 5`), called out in red.

10. **Methodology footnote** (verbatim): "FPD measures origination quality at the time of underwriting. A 30-day pawn loan that reaches 60–90 days past origination with zero customer activity is a clean signal that the loan should not have been written, the loan-to-value was too aggressive, or customer evaluation broke down."

═══════════════════════════════════════════════
STEP 6 — Success check and DM
═══════════════════════════════════════════════

Success criteria:

- All 5 stores have row-level CSVs captured (or clearly marked "Could not compute" for any pipeline failures).
- Archive `fpd-history.csv` updated with new ticket numbers.
- Slack message posted to `#first-payment-default` (`C0B17894S2Y`) with store ranking, this-week categories, AND chronic-risk categories.
- Word doc copied to `/Users/joshuadavis/Documents/Claude/Scheduled/FPD_Ranking_[YYYY-MM-DD].docx`.

If any store failed, send a brief DM to Joshua (`U03BB52MDSA`) with the trigger ID and which store(s) failed and why. The ops-channel post itself stays clean.

═══════════════════════════════════════════════
If something goes wrong
═══════════════════════════════════════════════

- **Watcher not running** (no result JSON and no CSVs after 40 min): DM Joshua the failure with the trigger ID and stop.
- **All 5 cells fail with EnsureStore or similar auth errors**: VM-side issue. DM Joshua. Don't keep retrying.
- **Saved report not found** (cell errors mention `SelectSavedReport` or `Claude First Payment Default`): the saved Bravo report doesn't exist or has been renamed. DM Joshua.
- **Some cells succeeded, others didn't**: post what you have to `#first-payment-default` with a `🎯 *Partial FPD Ranking — [today]*` header, list the missing stores in a trailing `_Note:_` line, and DM Joshua.
- **CSV column names changed** (parser can't find `Loan Amount` or `Category`): the saved Bravo report's columns have been edited. DM Joshua with the actual header row found.
- **Archive file corrupted** (cannot parse `fpd-history.csv`): proceed with the weekly run but skip the 12-month chronic blocks in this run's Slack post and docx; DM Joshua to repair.

═══════════════════════════════════════════════
Background — pipeline contract
═══════════════════════════════════════════════

The `fpd-cohort` report handler lives at `reports/FpdCohort.ahk` in the Bravo Data Extraction project. It runs the saved Bravo report "Claude First Payment Default" via the standard Loans/Buys → Custom Reports → Choose Saved Report → Ok flow, waits for the DataItem grid to render, then calls `WriteBuysGridToCsv` (defined in BuysFromPublic.ahk) to dump every row's columns to CSV.

The output CSV columns are whatever the saved Bravo report exposes. To change which columns are captured (e.g. add Loan Date, Customer ID), edit the saved Bravo report itself in any one store — it's shared company-wide.

═══════════════════════════════════════════════
History
═══════════════════════════════════════════════

- 2026-05-18 — Added 12-month rolling archive (`fpd-history.csv`) with weekly dedupe-by-ticket append; new Chronic-risk sections in both Slack post and Word doc.
- 2026-05-18 — Rewritten to consume **row-level** FPD CSVs (instead of count+sum aggregate). New per-store category breakdown and top-10 individual loans in the Word doc. Old aggregate flow backed up as `FpdCohort.ahk.bak-pre-rowlevel-2026-05-18`.
- 2026-05-18 — Initial rewrite to use the Bravo Data Extraction pipeline + the saved Bravo report "Claude First Payment Default" (count + sum aggregate version).
