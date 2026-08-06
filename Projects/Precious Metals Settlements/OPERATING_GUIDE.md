# Elemetal Precious Metals Settlement — Operating Guide

Read this file completely before doing anything. This is a fresh session with no memory of
prior runs — everything you need is here or discoverable via the tools listed.

## Mission

Every month Valley Pawn scraps gold/gold-stones/silver (1st–5th), ships it to Elemetal, and
gets settlement emails back (usually by the 10th, sometimes later) — typically 2–3 separate
emails/PDFs: one for plain gold, one for gold-with-stones, one for silver (if sent; silver is
often held back). Each store's share of a settlement is proportional to how much weight (dwt)
that store contributed to the total scrapped that month. This job:

1. Finds this month's Elemetal settlement email(s) + extracts the dollar figures from the PDFs
2. Loads each store's weight contribution from Bravo's scrap-refining-gold CSVs
3. Calculates each store's dollar allocation
4. Writes a REVIEW workbook (CSV) for Joshua to check and approve
5. Once Joshua renames it to CLOSED, archives everything to Drive and posts a Slack summary

**Out of scope, always:** QuickBooks / GL posting. That's handled entirely by Joshua's existing
monthly Bravo GL pull — this job never touches QBO.

## Tools you have

- `mcp__Gmail__search_threads` / `get_thread` — search/read Elemetal emails (CANNOT download
  attachment bytes — there is no attachment-download tool in this Gmail MCP surface)
- Claude in Chrome (`mcp__claude-in-chrome__*`) — use this to open Gmail in the browser
  (already logged in as jdavis@fcfpawn.com, do NOT ask Joshua to log in), open the PDF
  attachment preview, and download it. Downloaded files land in `~/Downloads` on the Mac.
- `mcp__remote-devices__Control_your_Mac__osascript` (or the equivalent local shell/osascript
  connector available in this session) — run `do shell script "..."` for all local file I/O:
  moving downloaded PDFs, reading Bravo CSVs, writing the workbook, archiving to Drive. This is
  how you reach files outside the scheduled-task sandbox — it's how daily-funds-verification
  and other Valley Pawn tasks read the Bravo Data Extraction output folder.
- `Read` tool — can open a local PDF file and view it as an image (multimodal). Use this to
  read the settlement PDFs directly rather than regex-parsing extracted text — the PDFs are
  clean, structured tables and vision reading is far more reliable than text extraction.
- `mcp__Slack__slack_send_message` — already authenticated, posts directly.

## Paths

- Project root: `/Users/joshuadavis/Documents/Claude/Projects/Precious Metals Settlements/`
  - `downloads/<YYYY-MM>/` — downloaded settlement PDFs for that month
  - `reviews/<YYYY-MM>_allocations_REVIEW.csv` — pending Joshua's review
  - `reviews/<YYYY-MM>_allocations_CLOSED.csv` — Joshua has approved (he renames REVIEW→CLOSED)
  - `archive/<YYYY-MM>/` — local copy after archiving
  - `logs/state.json` — tracks which Gmail message IDs have already been processed into a
    REVIEW workbook, so re-runs don't duplicate work. Read it first; write it back at the end.
- Bravo weight CSVs: `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/`
  — files named `<YYYY>_<STORE>_scrap-refining-gold.csv` for STORE in CUL, HAR, LEX, ROA, WAY.
  Columns: `Store,Month,BucketName,CreatedOn,Status,StatusDate,CombinedMetalWeightDwt`.
  **`Month` is formatted `YYYY-MM` (with the dash) — match it exactly, do not strip the dash.**
  Classify `BucketName` (case-insensitive) by substring: contains "STONE" → gold_stones;
  contains "SILVER" → silver; contains "GOLD" (and not "STONE") → gold.
- Drive archive destination (already a normal synced local folder — plain file copy, no API):
  `/Users/joshuadavis/Library/CloudStorage/GoogleDrive-jdavis@fcfpawn.com/Shared drives/Valley Pawn Drive/Accounting Exports/Precious Metals Settlements/<YYYY-MM>/`
- Slack channel: `#gold-trend-` (ID `C0BJ8SYTVBN`) — Joshua's existing precious-metals
  automation channel (also used by the gold-dwt-YOY job). Post there, not to a new channel.

## IMPORTANT: which month's weights match which month's settlement

Scrap happens 1st–5th of a month; settlement for that same batch typically arrives by the
10th of the **same** month. So: **settlement month == weight month.** Do not offset by one
month. Verify against the CSV's `Month` column and the settlement PDF's date — they should be
the same `YYYY-MM`.

## Step-by-step

### 1. Load state
`cat` `logs/state.json` (create it as `{"processed_message_ids": [], "archived_months": []}` if
missing) via osascript. This tells you what's already been done — don't redo it.

### 2. Determine target month
Default target = current calendar month (`YYYY-MM` from today's date). If it's very early in
the month (before the 5th), there may be nothing yet — that's fine, exit quietly after checking.
**A settlement email can arrive addressing a PRIOR month's still-open buckets** (this is exactly
the blended-settlement case — see step 7). So "the workbook you're building" is really keyed to
whichever month's Bravo buckets the new settlement is actually closing, which you determine from
Bravo's `Status` column, not necessarily the calendar month the email arrived in. Name the
REVIEW/CLOSED workbook after the scrap month being closed, not the email's arrival month, when
they differ.

### 3. Check for a CLOSED file needing archive (do this FIRST, every run)
For the current and prior 2 months, check `reviews/<month>_allocations_CLOSED.csv`. If it
exists and `<month>` is not yet in `archived_months`:
- Copy the CLOSED workbook + `downloads/<month>/*` to the Drive archive path (osascript
  `mkdir -p` then `cp`) and to `archive/<month>/`.
- Post a Slack summary to `#gold-trend-` via `mcp__Slack__slack_send_message`: total settlement,
  per-store payout, and the Drive path. Read the CLOSED CSV to build the summary numbers.
- Add `<month>` to `archived_months` in `logs/state.json` and write it back. Do this exactly
  once per month — check the list before posting so Slack doesn't get duplicate notifications.

### 4. If a REVIEW file already exists for the target month and is NOT closed
Do nothing — it's waiting on Joshua. Exit.

### 5. Otherwise, look for new settlement emails
`mcp__Gmail__search_threads` with query:
`from:noreply@elemetal.com after:<month>-01 before:<next-month>-01 has:attachment`
(also check the prior month's window once, in case an email arrived a few days late relative
to when scrap happened). Skip any thread whose message ID is already in `processed_message_ids`.

If none found: exit quietly (no Slack noise for "nothing yet" — this job runs daily and that's
expected most days).

### 6. Download and read each new settlement PDF
For each new message:
- Use Claude in Chrome: navigate to
  `https://mail.google.com/mail/u/0/#search/from%3Anoreply%40elemetal.com/<threadId>`,
  click the attachment thumbnail to open the PDF preview, and download it (there's a download
  icon in the preview toolbar, or use the browser's download shortcut).
- Via osascript, move the newly-downloaded file from `~/Downloads` into
  `downloads/<month>/` with a clear name (e.g. `<month>_<lotId>.pdf`).
- Use `Read` on that PDF file to view it (it renders as an image — read the numbers directly,
  don't try to regex raw text).

**What the PDF looks like** (confirmed against real July 2026 settlements — format is a clean
table, should be stable):
- Header: title like "Elemetal - Stone Removal" or "Elemetal - Norfolk" or "Elemetal - <lot
  name>" — the title is NOT a reliable metal-type indicator by itself (it's more of an
  Elemetal-internal facility/lot name). Use the `LOT-XXXXXXX <description>` line and the
  `Metal:` row instead — e.g. "LOT-2607062557186  Scrap Gold Stone Removal" with `Metal: Gold`
  further down, or "LOT-2607062557189  Scrap Gold Karat" with `Metal: Gold`.
- A weights table: `Pre-Melt` / `Post-Melt` rows with grams/dwt/ozt/lbs, and an `Amount` +
  `Settlement` column on that same row block (e.g. `$26,749.39` / `Pay`) — this is the GROSS
  settlement amount for that lot.
- `ACCOUNT BALANCE` section confirms the transaction amount.
- `PAYMENT` section: the actual `Amount` wired to Valley Pawn (net of the settlement, e.g.
  `$26,714.39`) — this is after `Charge Type` line items (shipping, processing fee) shown
  above, and a `PAYMENT FEE` (wire fee, usually -$20.00) shown below.
- **Use the PAYMENT section's net `Amount` as "the money we actually got"** for allocation
  purposes (this matches Joshua's own framing: "extract the amount of money we got as a
  whole"). The gross LOT `Amount` is useful context to include in the workbook but the net
  wire amount is what actually landed and is what should drive store payouts.

### 7. Classify each settlement into a bucket
Read the LOT description + Metal row:
- Description/metal clearly "Gold" with no stone/silver mention → bucket `gold`
- Description mentions "Stone" (e.g. "Stone Removal", "W/Stones") AND was assayed/settled as
  its own distinct lot from the plain-gold lot → bucket `gold_stones`
- Description mentions "Silver" → bucket `silver`

**Exception — blended settlements (confirmed real, e.g. Aug 2026 covering July buckets):**
sometimes Elemetal melts a stones lot and a no-stones lot down together and pays it out as one
settlement instead of the usual two — you get ONE PDF / ONE dollar amount that needs to close
out what are normally two separate open buckets. Do NOT guess which buckets it covers from the
PDF description alone. Instead, **use Bravo's own bucket `Status` column as the source of truth**:

1. Load the Bravo scrap-refining-gold rows for the relevant scrap month(s) — note the
   settlement can arrive in a *later* calendar month than the scrap it's closing out (this is
   the norm when it's late/blended — e.g. an early-August settlement closing out July's
   buckets). Don't assume settlement month == scrap month when a blend is suspected; check
   both the settlement's own month and the prior month for `OPEN` buckets.
2. Find every bucket with `Status == OPEN` for that store/period — these are the buckets still
   awaiting settlement. A normal (non-blended) month has exactly one open bucket-type being
   closed by a matching single-type settlement; a blended month has **multiple** open buckets
   (e.g. both a `GOLD SCRAP` and a `GOLD W/STONES SCRAP` bucket sitting OPEN) being closed by
   one settlement.
3. If one settlement's dollar amount lines up with exactly one OPEN bucket type across stores
   → treat it as clean (gold, gold_stones, or silver) as usual.
4. If it doesn't cleanly match one bucket type — multiple OPEN buckets exist for the period and
   only one settlement email arrived to close them — mark it `blended` and pool the dollar
   amount against the **combined weight of every OPEN bucket it's plausibly closing** (sum each
   store's dwt across those open buckets), allocating each store's share of that combined total.
5. Always state in the workbook, in plain English, exactly which open buckets (store + bucket
   name + dwt) were pooled and why, so Joshua can catch it immediately if it's wrong. When in
   doubt, flag as blended rather than force a clean-bucket guess — a flagged blended line is
   easy for Joshua to correct; a wrongly-assigned clean bucket silently misallocates money.
6. Bravo buckets don't close themselves — once Joshua approves the workbook (renames it to
   CLOSED), note in the archive step that the corresponding Bravo buckets should be marked
   closed too (this handler doesn't write to Bravo; just flag it clearly in the Slack
   archive-notification so Joshua or Preston can close them out in Bravo).

### 8. Load Bravo weights for the target month
Via osascript, `cat` each `<YYYY>_<STORE>_scrap-refining-gold.csv`. For a normal settlement,
filter rows where `Month == <target month>` and sum `CombinedMetalWeightDwt` per store per
bucket (gold / gold_stones / silver) using the BucketName classification above. For a
suspected-blended settlement, instead filter rows where `Status == OPEN` (regardless of exactly
which month, though usually the current or prior month) to find what's actually still awaiting
settlement — see step 7.

### 9. Calculate allocations
For each settlement (clean-bucket or blended):
```
store_$ = (store_weight_for_relevant_bucket(s) / total_weight_for_relevant_bucket(s)) × settlement_$
```
Do this independently per settlement, then sum each store's total across all of that month's
settlements for its grand total.

### 10. Write the REVIEW workbook
`reviews/<month>_allocations_REVIEW.csv` via osascript (build the CSV content, base64-encode
it, and `echo '<base64>' | base64 -d > 'path'` to avoid shell-quoting problems with `$`, `,`,
newlines). Include:
- Header with month + generated timestamp
- Total settlements section (one line per settlement: bucket/blend label, gross LOT amount,
  net PAYMENT amount used for allocation)
- Per-store allocation table: $ and % of weight per bucket, plus a grand total row
- Weight detail (dwt) per store per bucket, for verification
- Clear instructions: review, adjust $ if needed, rename REVIEW→CLOSED when approved
- Any blended-settlement notes from step 7, spelled out in plain English

### 11. Update state
Add the processed message IDs to `logs/state.json` and write it back via osascript.

### 12. Report
End your run with a short plain-text summary of what you did (found emails? wrote a workbook?
archived a closed one? nothing to do?) — this becomes the scheduled-task run's visible output.
Don't post to Slack for routine "nothing new" runs — only for a newly-archived CLOSED month
(step 3) or if something is broken and needs Joshua's attention (e.g., PDF format changed
unrecognizably, Bravo weight CSVs are missing entirely for the target month).
