---
name: weekly-loan-layaway-review
description: On-demand — run Bravo loan & layaway review across all 5 Valley Pawn stores via the Bravo Data Extraction pipeline. Post LOAN summary to #loan-review and LAYAWAY summary to #layaway-review (TWO separate posts, separate channels). No Parallels grant required.
---

Run the Valley Pawn weekly past-due loan and layaway review across all 5 stores.

═══════════════════════════════════════════════
STEP 1 — Drop the Bravo trigger and wait
═══════════════════════════════════════════════

Drop ONE trigger that fetches BOTH `loans-75-days-past-due` AND `layaways` for all 5 stores. Generate a trigger ID like `loan-layaway-review-YYYY-MM-DDTHH-MM-SS`. Write to `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/triggers/<id>.json`:

```json
{
  "id": "loan-layaway-review-2026-05-12T08-00-00",
  "requested_at": "2026-05-12T08:00:00-04:00",
  "reports": [
    {"name": "loans-75-days-past-due", "stores": ["CUL","HAR","LEX","ROA","WAY"], "date": "2026-05-12"},
    {"name": "layaways", "stores": ["CUL","HAR","LEX","ROA","WAY"], "date": "2026-05-12"}
  ]
}
```

Poll `results/<id>.result.json`. Full run takes ~5-8 minutes (10 cells × ~30-60s each). Time out at 15 minutes.

═══════════════════════════════════════════════
STEP 2 — Parse the CSVs
═══════════════════════════════════════════════

**Per-store loan CSV** (one row each): `store, date, count, dollar_sum`
- `count` is the post-filter count of loans matching the "75 Days Past Due" saved Ad Hoc report (counts the rendered list rows, not the sidebar widget)
- `dollar_sum` is the total $ exposure of those loans (from the summary panel)
- Both fields can legitimately be 0 if a store has nothing 75+ days past due — that's a ✅ clean store, not a missing read.

**Per-store layaway CSV** (one row each): `store, date, overdue, past_pmt_due, contacted_no_activity, no_pmt_30d, locate`
- All 5 badges captured from the Layaways view right panel

═══════════════════════════════════════════════
STEP 3 — Compute loan past-due percentages
═══════════════════════════════════════════════

Need per-store loan balance to compute `% of loan balance`. The Company KPI report has this. For now (until company-kpis report is built), pull this from the most recent monday-store-rankings post in #store-performance (Slack search: `in:#store-performance loan balance`) or from a cached Google Sheet. If not available, omit the % column and footer-note "Loan balance unavailable this run".

For each store: `pct = dollar_sum / loan_balance * 100`

═══════════════════════════════════════════════
STEP 4 — Post LOAN → #loan-review (`C0B08RS2BMK`)
═══════════════════════════════════════════════

```
📋 *Weekly Past-Due Loan Review — [DATE]*

*PAST DUE LOANS (75-day rule — cap 5% of loan balance)*
• *CUL* — [X] items / $[amount] / [X.XX]% [✅/🚨]
• *HAR* — [X] items / $[amount] / [X.XX]% [✅/🚨]
• *LEX* — [X] items / $[amount] / [X.XX]% [✅/🚨]
• *ROA* — [X] items / $[amount] / [X.XX]% [✅/🚨]
• *WAY* — [X] items / $[amount] / [X.XX]% [✅/🚨]
*Total past 75d:* [X] items / $[amount]
```

- ✅ when within the 5% threshold, 🚨 when over
- Every loan row carries both count and dollars
- If dollar total can't be captured for a store, write `$?` and add a footer "couldn't capture dollars for [STORE]"

═══════════════════════════════════════════════
STEP 5 — Post LAYAWAY → #layaway-review (`C04N24STDP1`)
═══════════════════════════════════════════════

```
📋 *Weekly Layaway Review — [DATE]*

Store          Overdue   Past Pmt Due   Contacted/No Act   30d-No-Pmt   Locate
─────────────  ───────   ────────────   ────────────────   ──────────   ──────
Culpeper          [X]         [X]             [X]              [X]         [X]
Harrisonburg      [X]         [X]             [X]              [X]         [X]
Lexington         [X]         [X]             [X]              [X]         [X]
Roanoke           [X]         [X]             [X]              [X]         [X]
Waynesboro        [X]         [X]             [X]              [X]         [X]
─────────────  ───────   ────────────   ────────────────   ──────────   ──────
Company           [X]         [X]             [X]              [X]         [X]
```

- Use fenced code block in Slack for column alignment
- Company row = sum each column across all 5 stores
- If any store's Locate count is non-zero, prefix the Company-row Locate with 🔴 (e.g., `🔴2`)

After the table, list **action items** as bullets — one bullet per non-zero Locate (`🔴 *[STORE] has [X] Locate Layaway(s)* — must be physically located and resolved`).

Close with source line: `_Source: Bravo POS · Layaways view detail badges captured per store: Layaways Overdue · Past Payment Due Date · Contacted But No Activity · No Payment in 30 days · Locate Layaways. Companion loan review in <#C0B08RS2BMK|loan-review>._`

═══════════════════════════════════════════════
STEP 6 — Save the Word doc
═══════════════════════════════════════════════

Save `Loan_Layaway_Review_[YYYY-MM-DD].docx` to `/Users/joshuadavis/Documents/Claude/Scheduled/` with BOTH loan and layaway sections. The doc structure is unchanged — only the data collection method moved to the pipeline.

═══════════════════════════════════════════════
DEPRECATED FORMATS — DO NOT USE
═══════════════════════════════════════════════

- ❌ Single combined post to one channel
- ❌ Posting to `#performance`, `#store-performance`, `#claude-updates`, or `#layaway-and-loan-review`
- ❌ Substituting item counts for dollar totals when dollar capture fails
- ❌ Reading layaway counts off the Dashboard right-sidebar widgets — the Layaways VIEW badges are the source of truth and the pipeline reads them correctly

## Background

Before 2026-05-12 this task drove Bravo via Parallels + computer-use. The pipeline now produces both the 75-day past-due loan data and the layaway badge counts as CSVs.
