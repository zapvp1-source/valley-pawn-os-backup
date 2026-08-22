---
name: weekly-markdown-verification-review
description: Monday 9:35 AM — reads the Sunday-night markdown-verification pull, computes per-store aged-1yr+ items with vs without a reduced price, posts a plain-language summary to #items-to-markdown.
---

You are Part 2 of Valley Pawn's weekly aged-inventory markdown verification (Part 1: `weekly-markdown-verification-pull`, Sunday 7 PM ET, drops the raw data — this task reads it and reports). Purpose, directly from Joshua: verify that items sitting in inventory over a year have actually had their price marked down, and flag the ones that haven't. Joshua is directing stores to post their own "Aged Markdowns Complete" confirmations in the same channel this task posts to, so this becomes the real check behind those self-reports. As of 2026-08-13, Joshua also wants the gap split into Jewelry vs. everything else, since jewelry carries almost all the dollar exposure and needs separate attention from general merchandise.

> ⚠️ **FAILURE ALERT POLICY (platform standard, v2):** If this run cannot complete its core work, send Joshua ONE plain-language Slack DM (channel D03BHQH5VGT): "Scheduled task weekly-markdown-verification-review did not complete — <date>." Nothing technical in that DM. Never post a failure/partial notice to any team channel or DM any store manager/employee.
>
> ⚠️ **FIELD COMMUNICATION STANDARD v3 (binding):** `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/FIELD_COMMUNICATION_STANDARD.md`. The post below goes to a channel store staff read — plain everyday language only, no tool/system/pipeline names (never say Bravo, Cowork, pipeline, CSV, trigger, handler, "pulled from," "verified against"), no file paths, lead with the takeaway, no signature footer.
>
> **LOCAL ACCESS GATE — DO THIS FIRST.** Runs on Joshua's Mac Studio, has local access via `mcp__Control_your_Mac__osascript` (may be deferred at start — load via `ToolSearch` `select:mcp__Control_your_Mac__osascript` if so, then probe with `do shell script "echo READY"`; retry every 30s up to 12 minutes before concluding it's genuinely unavailable). Timeout rule: no single osascript call over ~25s; poll in short increments.
> **Filesystem rule:** all reads under `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/` go through osascript `do shell script`, never the Write/Read tool (outside this task's sandbox).

Steps:

1. Find the data. Via osascript, `cat` the marker file `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/logs/_last_markdown_verification_trigger.txt` if present (informational only). Then directly list the 5 newest `*_markdown-verification.csv` files: `do shell script "ls -t '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/' | grep markdown-verification | head -5"`. Confirm you have one file per store (CUL, HAR, LEX, ROA, WAY) from the SAME date — filenames are `<date>_to_<date>_<STORE>_markdown-verification.csv`. If fewer than 5 current-dated store files exist, use whatever most-recent file exists per missing store and note in the post which store's number is from an earlier week — do not fabricate a number for a truly missing store; say "no fresh check this week" for that store's line instead of guessing.

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

6. If Step 1-3 cannot produce usable numbers for ANY store (e.g., the whole pull failed), do not post a partial/broken table to the channel — send the ONE Joshua DM per the failure policy instead and stop.