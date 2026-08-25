---
name: weekly-markdown-verification-review
description: Monday 9:35 AM — reads the Sunday-night markdown-verification pull, computes per-store aged-1yr+ items with vs without a reduced price, posts a plain-language summary to #items-to-markdown.
model: claude-sonnet-5
---

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
You are Part 2 of Valley Pawn's weekly aged-inventory markdown verification (Part 1: `weekly-markdown-verification-pull`, Sunday 7 PM ET, drops the raw data — this task reads it and reports). Purpose, directly from Joshua: verify that items sitting in inventory over a year have actually had their price marked down, and flag the ones that haven't. Joshua is directing stores to post their own "Aged Markdowns Complete" confirmations in the same channel this task posts to, so this becomes the real check behind those self-reports. As of 2026-08-13, Joshua also wants the gap split into Jewelry vs. everything else, since jewelry carries almost all the dollar exposure and needs separate attention from general merchandise.

> ⚠️ **FAILURE HANDLING — Rule 16 (supersedes the old v2 Failure Alert Policy, updated 2026-08-24):** **Do NOT send a failure DM. Not to Joshua, not to any channel.** The previous version of this line told the run to DM Joshua "Scheduled task weekly-markdown-verification-review did not complete — <date>." That is now a rule violation: it is a technical failure notification naming an internal task, and Joshua has said explicitly that failure notices and tech jargon must never go to Slack. On 2026-08-24 that exact DM also fired *wrongly* — a full week of good data was on disk. If this run genuinely cannot produce numbers after exhausting the Step 1b retry, write what happened to `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/BRAVO_KNOWN_ISSUES.md` and stop silently. Joshua reads status files when he wants them. Never post a failure or partial notice to any team channel, and never DM a store manager or employee.
>
> ⚠️ **FIELD COMMUNICATION STANDARD v3 (binding):** `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/FIELD_COMMUNICATION_STANDARD.md`. The post below goes to a channel store staff read — plain everyday language only, no tool/system/pipeline names (never say Bravo, Cowork, pipeline, CSV, trigger, handler, "pulled from," "verified against"), no file paths, lead with the takeaway, no signature footer.
>
> **LOCAL ACCESS GATE — DO THIS FIRST.** Runs on Joshua's Mac Studio, has local access via `mcp__Control_your_Mac__osascript` (may be deferred at start — load via `ToolSearch` `select:mcp__Control_your_Mac__osascript` if so, then probe with `do shell script "echo READY"`; retry every 30s up to 12 minutes before concluding it's genuinely unavailable). Timeout rule: no single osascript call over ~25s; poll in short increments.
> **Filesystem rule:** all reads under `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/` go through osascript `do shell script`, never the Write/Read tool (outside this task's sandbox).

Steps:

1. Find the data — resolve the newest file **per store**, never a global `head -5`. Run this exact one-liner:

```
do shell script "cd '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output' && for s in CUL HAR LEX ROA WAY; do f=$(ls -t *_${s}_markdown-verification.csv 2>/dev/null | head -1); echo \"$s ${f:-NONE}\"; done"
```

   Filenames are `<date>_to_<date>_<STORE>_markdown-verification.csv`. Then read the marker file `logs/_last_markdown_verification_trigger.txt` and the matching `results/<trigger-id>.result.json` — **the result JSON is the authoritative record of which stores actually succeeded**, listing per-store `status`, `row_count`, `output_path` and `error`. Read it before concluding anything about a store.

   > ⚠️ **HARDENING (2026-08-24) — never revert to `ls -t '<output>/' | grep markdown-verification | head -5`.** On 2026-08-24 that command returned a stale, partial directory listing: it showed only the 2026-08-13 files and completely hid the newer 2026-08-21 (5/5 stores) and 2026-08-23 (3/5 stores) sets that were sitting right there on disk. The run concluded "no fresh data this week," skipped the report, and sent Joshua a false failure DM — a full week of real data was on disk the whole time. Root cause: `output/` holds ~2,200 files and is written by the Windows VM through a Parallels shared folder, so directory enumeration can lag or truncate. **A "no files found" result is NOT sufficient evidence that the pull failed.** If any store resolves to NONE, you MUST confirm with an independent command before acting on it — `find '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction' -name '*markdown-verification*.csv'` walks the tree directly and did not exhibit the stale listing. Only after `find` also comes back empty may you treat data as genuinely missing.

1b. **If any store is missing, stale, or errored in the result JSON — re-pull it. Do not just report it (Rule 15, fix-forward).** The pipeline handler is `markdown-verification` and the trigger queue is safely serialized, so a retry drop is low-risk and needs no contention check. Write a trigger naming ONLY the failed stores:

```
do shell script "cd '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/triggers' && cat > 'markdown-verification-retry-<UTC-id>.json' <<'EOF'
{
  \"id\": \"markdown-verification-retry-<UTC-id>\",
  \"requested_at\": \"<ISO8601 -04:00>\",
  \"reports\": [
    {\"name\": \"markdown-verification\", \"stores\": [\"LEX\",\"ROA\"], \"date\": \"<today YYYY-MM-DD>\"}
  ]
}
EOF"
```

   Then poll for completion — the trigger moves `triggers/` → `claimed/` → `processed/`, and `logs/<id>.log` plus `results/<id>.result.json` appear. Budget ~150–260s **per store**, and note the watcher processes one trigger at a time, so if another job is already claimed you will wait for it to finish first. Poll in ≤18s sleeps (the osascript wrapper kills calls over ~25s) for up to ~20 minutes. If the retry lands, use the fresh numbers. If it does not land in time, fall back to the most recent file per store and note in the post which store's number is from an earlier week — do not fabricate a number. Only if a store has NO file at all, ever, does its bullet become "no fresh check this week."

2. Read each CSV via osascript `cat` (or a short inline `python3 -c '...'` one-liner if that parses more reliably — quoted commas appear in some Description fields). Columns are exactly: `Number,Status,Category,Description,Price,Sale Price,Cost,Date` (confirmed live 2026-08-13).

3. Compute, per store:
   - Only rows where `Status` = `INVENTORY` (skip other status values defensively).
   - Parse `Date` as `M/D/YYYY`. Age in days = (today − Date). "Aged 1yr+" = age >= 365 days.
   - Among aged 1yr+ rows: `marked_down` = rows where `Sale Price` is non-empty/non-zero; `not_marked_down` = rows where `Sale Price` is empty. Only `not_marked_down` rows matter for the report.
   - **Jewelry vs General Merch split (added 2026-08-13, validated live against the real category list):** classify each `not_marked_down` row's `Category` value:
     - JEWELRY if the category text (case-insensitive) contains any of: `gold`, `silver`, `platinum`, `diamond`, `gent's`, `lady's`, `unisex`, `wristwatch`, `pocket watch`, `necklace`, `pendant`, `bracelet`, `earring`, `brooch`, `charm`, `ring`, `chain`
     - EXCEPT force these to GENERAL MERCH even if they matched a keyword above: `smart watch`, `fashion accessory`, `men's accessory`, `accessories`, plain `coin` (with no gold/silver qualifier)
     - Everything else not matched = GENERAL MERCH.
     - This was spot-checked live 2026-08-13 (Harrisonburg's 56 not-marked-down items were 100% silver/gold ring/pendant/chain/earring categories — classifier held up under inspection). If a category shows up that seems ambiguous, classify by this rule mechanically rather than guessing case-by-case — consistency week to week matters more than a perfect edge case call.
   - `jewelry_count` / `jewelry_dollars` and `genmerch_count` / `genmerch_dollars` = count and sum of `Price` (strip `$`,`,`) for each bucket, per store.
   - `not_marked_down_dollars` (store total) = jewelry_dollars + genmerch_dollars.
   - Company totals = sum across all 5 stores, for jewelry, general merch, and combined.

4. Post to Slack channel `C0BQX7CF13J` (#items-to-markdown — renamed from #mark-downs-summary by Joshua on 2026-08-14; same channel ID, this remains the permanent home for this report; store managers post their own "Aged Markdowns Complete" confirmations here too, so this is the automated cross-check sitting alongside them) via `slack_send_message`. Plain language, per the Field Communication Standard — no jargon, no store-blame tone. Lead with the combined takeaway, then the jewelry/general-merch split (jewelry is normally the much bigger dollar problem — call that out same as the company total), then per-store. Shape (adapt numbers, keep this concise — this is the locked format going forward):

```
:label: Markdown check — [DATE]
[X] items sitting over a year still haven't been marked down — $[Y] worth.

Jewelry: [n] items, $[d]
General merch: [n] items, $[d]

By store:
• Culpeper: [n] ($[d])
• Harrisonburg: [n] ($[d])
• Lexington: [n] ($[d])
• Roanoke: [n] ($[d])
• Waynesboro: [n] ($[d])

[One short line calling out whichever store or bucket is the biggest driver this week — e.g. "[Store] alone is nearly two-thirds of the jewelry total — worth a look first." Only include this line if one store/bucket is clearly disproportionate; omit if it's evenly spread.]
```
If a store had no fresh check this week (from step 1), replace its bullet with "• [Store]: no fresh check this week" — do not give it a 0.

5. Also DM Joshua (not the channel) one extra line the channel post does not carry, since he specifically asked to see trend/frequency, not just a snapshot: "Markdown check [DATE]: company-wide [X] items / $[Y] still not marked down (jewelry $[Yj] / general merch $[Ym]) — was [prior week's totals] if available, otherwise 'first run with the jewelry split, no prior week to compare yet'. Note: the report doesn't currently record WHEN an item was last marked down, only whether it currently has a reduced price — so this can't yet show whether markdowns are actively continuing vs. static. Ask Preston whether a last-price-change date can be added to the report if you want that." Save this run's totals to the running history file `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/logs/_markdown_verification_history.csv` (append one row per store: `date,store,not_marked_count,not_marked_dollars,jewelry_count,jewelry_dollars,genmerch_count,genmerch_dollars` — via osascript; this file already has a 2026-08-13 baseline row per store in this exact format) so next week's DM can actually compare instead of asking Joshua to remember.

6. If Step 1b's retry still cannot produce usable numbers for ANY store, do not post a partial or broken table to the channel and **do not send any Slack failure message** (Rule 16). Log what happened to `BRAVO_KNOWN_ISSUES.md` and stop. If SOME stores have numbers and others don't, that is not a failure — post the report with the stores you have and mark the rest "no fresh check this week," per Rule 15's skip-and-continue.
