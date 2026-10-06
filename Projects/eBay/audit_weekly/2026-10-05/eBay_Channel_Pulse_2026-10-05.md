# eBay Channel Pulse — 2026-10-05 (PARTIAL RUN — no live pull)

**This run could not reach the eBay Trading API.** This Cowork sandbox session has no bridge to
`~/.vp_secrets/ebay_store_tokens.py` / `~/ebay_weekly_rankings.py` and no Control_your_Mac/osascript
bridge (confirmed absent via ToolSearch). Logged to `FAILURE_LEDGER.md` (2026-10-05 11:45 ET,
`NEEDS_HUMAN: no`). This is the **second consecutive missed live pull** — the 2026-09-28 run hit
the identical wall. The underlying listings/fees/sold/messages dataset below is carried forward from
the **2026-09-07 full live pull** (28 days old) and is **not current**. Feedback score and Seller
Standards figures are refreshed from the **2026-10-02 headless ratings sweep** (3 days old), the
freshest real data found in the project folder.

## Headline (carried forward from 09-07, NOT a fresh pull — see note above)

| Metric | Value (09-07 data) | vs prior run |
|---|---:|---|
| Active listings | **446** (09-07) / **453** per last known-state 9/4 | not measurable — no fresh pull |
| Listed value | **$71,464** | not measurable |
| Sold, 90d | **572 units / $86,762** | not measurable |
| Fees, 90d | **$14,485 (16.7% of revenue)** | not measurable |
| Aged >90d | **199 listings / $20,146** | not measurable |
| Unread messages, 60d | **382** (27 return/refund, 1 case/dispute) | not measurable |
| Open Best Offers | **4**, all same-day-expiring on 9/7 — stale | not measurable |
| Markdown-capped, no action | **133** (Culpeper 101, Roanoke 18, HAR 8, LEX 6) | not measurable |

## What DID change this week (confirmed via the fresher 10-02 ratings sweep)

- **Harrisonburg dropped to Below Standard** at the 2026-09-21 seller-standards eval — defect rate
  5.23% (9/172) and cases closed without seller resolution 2.33% (4/172) are both over threshold.
  Next eval ~2026-10-20. **New flag this run** — logged to the Open Items Register and the
  marketing open-items register (CHANGELOG 2026-10-05, `DEC-EBAY-HAR-SHIP`).
- **Lexington resolved** — was Below Standard (late shipments) through the task brief's known state
  (as of 9/4, re-eval expected 9/20); the 9/21 eval moved it to **Above Standard**. Confirmed in
  CHANGELOG 2026-10-05 and the 10-02 sweep. No action needed.
- **Top Rated unchanged:** Culpeper + Waynesboro still Top Rated (US). Roanoke still not Top
  Rated (Above Standard, feedback score 5,744, 99.68% 12-mo positive — strongest feedback in the
  channel but dispatch time and TRS mechanics keep it below the bar, per the 09-07 note on 3-day
  Roanoke dispatch).

## Per-store table (listings/fees/sold = 09-07 data; standards/feedback = 10-02 data)

| Store | Active (09-07) | Listed value | Sold 90d (units/$) | Fees 90d | Fee % | Aged >90d ($) | Seller Standard (9/21 eval) | Feedback score (10/2) |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| Culpeper | 258 | $36,859 | 243 / $29,495 | $4,851 | 16.4% | $14,562 (142) | TOP_RATED | 1,317 |
| Waynesboro | 36 | $12,380 | 59 / $13,906 | $1,829 | 13.2% | $0 (0) | TOP_RATED | 632 |
| Harrisonburg | 32 | $6,818 | 51 / $10,474 | $1,841 | 17.6% | $729 (13) | **BELOW_STANDARD** | 629 |
| Lexington | 26 | $5,298 | 61 / $12,795 | $2,715 | 21.2% | $1,219 (13) | ABOVE_STANDARD | 1,284 |
| Roanoke | 94 | $10,109 | 157 / $20,092 | $3,249 | 16.2% | $3,637 (31) | ABOVE_STANDARD | 5,744 |
| **Channel** | **446** | **$71,464** | **572 / $86,762** | **$14,485** | **16.7%** | **$20,146 (199)** | 2 Top Rated / 2 Above / 1 Below | — |

## Flags

1. **Harrisonburg Below Standard (new)** — defect rate + cases-without-resolution both over
   threshold. Needs a human look before the ~10/20 re-eval. Logged to Open Items Register.
2. **Lexington resolved** — no action needed, informational.
3. **Stale-data risk** — two missed live pulls in a row (9/28, 10/5). The listings/fees/sold/
   messages/markdown dataset is now 28 days old. If this continues, the trend line this audit is
   supposed to build stops being meaningful. `NEEDS_HUMAN: yes` — someone with host access needs
   to build the allowlisted host_queue eBay-audit script recommended on 9/28 (still not built).
4. **Markdown-capped-at-30%, no further action (133 listings, carried forward from 09-07)** — not
   re-verified this run; per the 09-07 note this was a pre-cleanup snapshot, not necessarily a
   persistent backlog. Needs re-confirmation on the next live pull.
5. **Open Best Offers (4, carried forward from 09-07)** — all were same-day-expiring on 9/7 and are
   almost certainly stale/resolved by now one way or another. Cannot verify without a live pull.

## DATA SOURCE / LIMITATIONS

- **No live eBay Trading API pull this run.** Checked for an MCP eBay connector (none found),
  checked for fresher CSV/JSON exports in `Projects/eBay/` (none newer than 2026-09-10 except the
  10-02 ratings-sweep markdown and unrelated engine/script files), and confirmed no
  Control_your_Mac/osascript bridge is available in this session (per ToolSearch).
- **Listings, listed value, aging buckets, sold-90d, fees-90d, buyer messages, open Best Offers,
  markdown-capped-no-action:** all carried forward from `audit_weekly/2026-09-07/summary.json`
  (28 days old). Not current. Known gap from that run also carries forward unchanged: `GetMyeBaySelling`
  bulk response returns blank quality fields (photos/specifics/Best Offer/returns/dispatch), so those
  figures were themselves sample-based estimates even on 09-07.
- **Feedback score, 12-mo positive %, Seller Standards (level, late shipment, defect rate, cases
  w/o resolution, tracking on-time):** refreshed from `ebay-ratings-sweep-2026-10.md`, a headless
  pull run 2026-10-02 — 3 days old, the freshest real data available.
- **Not pulled at all this run (same gap as 09-07):** eBay Store subscription tier confirmation,
  Promoted Listings fee detail beyond the 09-07 figure, precious-metal aged-review cross-reference
  against `~/ebay_markdown_state.json` (unreachable — lives on the Mac home directory, not in this
  sandbox).
- **Trend comparison:** no true week-over-week delta exists for the stale fields (nothing changed
  because nothing was re-measured). The only real trend this run is the Seller Standards swing
  (Harrisonburg down, Lexington up), visible only because the 10-02 sweep happened to be fresher.
