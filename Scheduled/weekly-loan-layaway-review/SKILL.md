---
name: weekly-loan-layaway-review
description: On-demand — run Bravo loan & layaway review across all 5 Valley Pawn stores via the Bravo Data Extraction pipeline. Post LOAN summary to #loan-review and LAYAWAY summary to #layaway-review (TWO separate posts, separate channels). No Parallels grant required.
---

> ⚠️ **FAILURE POLICY — DO NOT POST TO SLACK ON FAILURE.** If this task fails, errors out, or cannot complete its intended work for any reason, DO NOT post anything to Slack — no error messages, no partial results, no "I couldn't finish" notices. Joshua reviews every run inside Claude to confirm success or failure, so a failed run must stay completely silent on Slack. Only post to Slack once the task has genuinely completed the work it was designed to do. Posting failure or error noise clutters Slack and reflects poorly on the team.

Run the Valley Pawn weekly past-due loan and layaway review across all 5 stores.

**STANDING RULE — DATA ONLY in the Slack posts.** The operations team reads `#loan-review` and `#layaway-review`. They do not need source footers, process commentary, or pipeline status notes. Post the title, the bullet list / table, and any 🔴 action items. Strip the `_Source: Bravo POS · ..._` footer and the `Companion ... review in <#...>` cross-link. The standing rule is: data and action items only — nothing about HOW the data was gathered or what went wrong. (Pipeline status / partial-data commentary belongs in the DM to Joshua, not the ops channel.)

**LOAN POLICY (revised 2026-05-13 per Joshua — definitive).**

The rule: *75-day past-due loan value cannot exceed 5% of the store's existing total loan balance.*

Per-store row format on the Slack post:
```
• *[STORE]* — [N] loans / $[past-due value] / [X.XX]% [✅ or 🔴]
```
where:
- `N` = count of loans 75+ days past due (from Bravo "75 Days Past Due" saved Custom Report, "Specific: N" header)
- `past-due value` = dollar sum of those loans (from the report's summary panel)
- `%` = `past-due value / current total loan balance × 100`
- ✅ if `% ≤ 5%` (within policy)
- 🔴 if `% > 5%` (out of policy)

For any store with 🔴, add an action line under the bullet list:
`🔴 *[STORE]* is [X.XX]% past 75 days — out of the 5% policy. Needs to be caught up.`

**Total loan balance (the % denominator) source.** The per-store total loan balance MUST come from Slack history — the SSRS company-kpis path is blocked by Bravo's Akamai bot-protection (`x-bni-fpc`/`x-bni-rncf` cookies set by client-side JS that we cannot replicate without a headless browser; see `reports/CompanyKpis.ahk` header in the Bravo Data Extraction project for the full diagnosis). Options in priority order:
1. Most recent `monday-store-rankings` post in `#store-performance` (Slack search: `in:#store-performance loan balance`).
2. Cached value in `/Users/joshuadavis/Documents/Claude/Scheduled/_shared-bravo-data/store-loan-balances.json` if it exists and is < 7 days old.
3. Ask Joshua directly.

If no source is available, post the count + dollar columns but show `%: n/a` and footer-note `_Loan balance unavailable this run — cannot evaluate against 5% policy._` (so the data is still useful even if we can't grade against policy yet).

**LOAN DATA SOURCE — IMPORTANT.** Per Preston (2026-05-13): there is a saved "75 days past due" report in Bravo's *Loans / Buys → Custom Reports*. The watcher's `Loans75DaysPastDue.ahk` handler MUST run that saved report, not synthesize the data by filtering an Ad Hoc query. If yesterday's all-zero loan results look suspicious, the handler may not be using the saved report — flag this in the DM to Joshua and verify before trusting the numbers.

**LAYAWAY DATA SOURCE — IMPORTANT.** Per Preston (2026-05-13): the red-bubble badge counts on the Layaways view's right sidebar are NOT always up to date. The correct method is to **click each category on the right** (Layaways Overdue / Past Payment Due Date / Contacted But No Activity / No Payment in 30 days / Locate Layaways) and read the count from the TOP of the screen for each filtered view. The watcher's `Layaways.ahk` handler currently pulls the red-bubble values. Until the handler is fixed, layaway counts may be off — flag this in the DM to Joshua so the ops channel post is held back or annotated until the data is verified.

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
