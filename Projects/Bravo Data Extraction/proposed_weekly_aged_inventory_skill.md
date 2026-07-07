---
name: weekly-aged-inventory-report
description: Pull aged inventory data from Bravo POS for all 5 Valley Pawn locations, update the Aged Inventory Google Sheet, and post a summary to Slack #aged-inventory-review. Pipeline-driven — no Parallels grant required.
---

## Valley Pawn — Weekly Aged Inventory Report

**OBJECTIVE**: Pull aged inventory data via the Bravo Data Extraction pipeline (which drives Bravo from inside the Windows VM), update the Aged Inventory Rankings Google Sheet with fresh data ranked by highest % aged, and post a formatted summary to Slack #aged-inventory-review.

**How this task works now:** the data collection runs through the trigger-file pipeline. This task drops one trigger file, waits for 5 CSVs, computes the metrics, then posts to Slack and updates the Google Sheet. Zero Parallels grant, zero computer-use.

---

## STEP 1 — Drop the Bravo trigger and wait

The pipeline lives at `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/`. The AHK watcher inside the Windows VM polls `triggers/*.json` every 30 seconds.

**1a. Generate a trigger ID** using today's date and a timestamp suffix:
```
aged-inventory-YYYY-MM-DDTHH-MM-SS
```

**1b. Write the trigger file** at `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/triggers/<id>.json`:

```json
{
  "id": "aged-inventory-2026-05-12T08-00-00",
  "requested_at": "2026-05-12T08:00:00-04:00",
  "reports": [
    {
      "name": "aged-inventory-summary",
      "stores": ["CUL", "HAR", "LEX", "ROA", "WAY"],
      "date": "2026-05-12"
    }
  ]
}
```

**1c. Poll for completion.** Watch for `results/<id>.result.json` to appear. Use bash `ls` checks every ~30 seconds. The full 5-store cycle takes ~3-5 minutes. Time out at 10 minutes.

If a cell's `status` is anything other than `success`, treat that store as "could not collect data" — note in the post body but continue.

---

## STEP 2 — Parse the CSVs

For each successful cell, read its CSV from the `output_path` in the result JSON.

The Aged Inventory Summary CSV is a DevExpress export with header rows + data rows. The data table has columns:
- Category | Qty | Cost | Price | <6mo | 6mo-1yr | 1yr-18mo | 18mo-2yr | 2yr-3yr | >3yr

Find the **Jewelry** row and the **Mfg. Goods** row. For each:
- Aged $ = `1yr-18mo` + `18mo-2yr` + `2yr-3yr` + `>3yr`

Find the **Subtotals** row and capture the Cost cell — that's the Inventory Balance for the % calculation.

Per-store, compute:
- `Aged Jewelry $` = sum of the four aged-over-1yr buckets in Jewelry row
- `Aged Merch $` = sum of the four aged-over-1yr buckets in Mfg. Goods row
- `Total Aged $` = Aged Jewelry $ + Aged Merch $
- `Inventory Balance (Cost)` = Subtotals row Cost

⚠️ **DO NOT use the "Aged Jewelry Markdown" / "Aged General Merchandise Markdown" custom reports.** Aged Inventory Summary is the source of truth.

---

## STEP 3 — UPDATE GOOGLE SHEET

Navigate Chrome to:
`https://docs.google.com/spreadsheets/d/1zSJhp0qfkD-2g4RSGNuXrcRh5bsi6vrRl45HQSMcsEY/edit`

The sheet "Valley Pawn - Aged Inventory Rankings" has this structure:
- Row 1: Headers (frozen) — Rank | Store | Inv. Balance | Aged Jewelry $ | Jewelry % | Aged Merch $ | Merch % | Total Aged $ | Total % Aged
- Rows 2–6: One row per store, ranked by Total % Aged (highest first)
- Row 7: TOTAL row with SUM formulas

Column layout:
- A=Rank, B=Store, C=Inv. Balance, D=Aged Jewelry $, E=Jewelry % (formula), F=Aged Merch $, G=Merch % (formula), H=Total Aged $ (formula), I=Total % Aged (formula)

Steps:
1. Calculate Total % Aged per store: (Aged Jewelry $ + Aged Merch $) / Inv. Balance
2. Sort all 5 stores highest to lowest by that percentage
3. Clear rows 2–6 columns A, B, C, D, F only (do NOT touch E, G, H, I — they are formulas)
4. Enter each store in ranked order: A=rank number, B=store name, C=inventory balance, D=aged jewelry $, F=aged merch $
5. Verify row 7 TOTAL formulas are still computing

---

## STEP 4 — POST TO SLACK

Use `slack_send_message` with channel `C04NGH4FF35` (#aged-inventory-review).

**⚠️ CANONICAL FORMAT — DO NOT DEVIATE.** Use the code-block table layout below exactly.

Computed columns:
- `J%` = Aged Jewelry $ / Inv. Balance, rounded to 2 decimals
- `GM%` = Aged Merch $ / Inv. Balance, rounded to 2 decimals
- `Tot%` = (Aged Jewelry $ + Aged Merch $) / Inv. Balance, rounded to 2 decimals

Rows ranked highest-to-lowest by Tot%.

Post message body:

```
📊 _Aged Inventory Review — [DATE]_
_Inventory Aged Over 1 Year (Cost Basis)_
_Ranked by Total Aged % of Inventory_

​```Store           Jewelry      J%       Gen Merch    GM%      Total        Tot%
─────────────   ──────────   ──────   ──────────   ──────   ──────────   ──────
[Store1]        $X,XXX.XX    XX.XX%   $X,XXX.XX    X.XX%    $XX,XXX.XX   XX.XX%
[Store2]        ...
[Store3]        ...
[Store4]        ...
[Store5]        ...
─────────────   ──────────   ──────   ──────────   ──────   ──────────   ──────
TOTAL           $XX,XXX.XX   XX.XX%   $XX,XXX.XX   X.XX%    $XX,XXX.XX   XX.XX%​```

_Key Takeaways:_
• [3–4 narrative bullets — call out highest %, biggest movers, anchor store at bottom]

📎 Full spreadsheet: <https://docs.google.com/spreadsheets/d/1zSJhp0qfkD-2g4RSGNuXrcRh5bsi6vrRl45HQSMcsEY|Valley Pawn Drive › Aged Inventory>
_Source: Bravo POS · Aged Inventory Summary report_
```

Format rules (locked in 2026-05-04):
- Table inside triple-backtick code block (Slack column alignment)
- Use `_italics_` for title and store names, not `*bold*`
- Footer source line: `Bravo POS · Aged Inventory Summary report` — exact phrase
- Do NOT use emoji ranking (1️⃣ 2️⃣ 3️⃣) — wrong format for this channel

**Week-over-Week Movement section is OPTIONAL.** If last week's data is readily accessible, include `_Week-over-Week Movement (vs [LAST WEEK DATE]):_` with one bullet per store. If not, omit.

---

## SUCCESS CRITERIA
- Rows 2–6 of the sheet updated with fresh data, ranked by Total % Aged
- TOTAL row (row 7) computing correctly
- Formatted Slack message posted to #aged-inventory-review

## If something goes wrong

- **Watcher not running** (no result JSON after 10 minutes, no CSVs): DM Joshua a brief failure note with the trigger ID and stop. He'll restart the watcher in the VM.
- **Some cells succeeded, others didn't**: post what you have, note the missing stores at the bottom of the message.

## Background

Before 2026-05-12 this task drove Bravo via Parallels + computer-use. The Bravo Data Extraction pipeline now produces the same Aged Inventory Summary CSV per store on demand. No UI grant needed.
