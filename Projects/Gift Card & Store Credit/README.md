# Gift Card & Store Credit — monthly report (by store)

Built 2026-09-29 at Joshua's request ("information on gift card and store credit by store … monthly publishing").

## Where the data comes from (Bravo, via the existing pipeline — no screen driving)
| Pipeline cell | Bravo report | Trigger date | Gives |
|---|---|---|---|
| `credit-balance` | Reports → Credit Balance | **single date = month-end** (a range uses the START date — wrong) | every open store credit, gift card and layaway credit, with issuing store, as of end of that day |
| `credit-journal` | Reports → Credit Journal | `START..END` | beginning balance, every issue/redemption with store + employee, ending balance |

Handlers `reports/CreditBalance.ahk` / `reports/CreditJournal.ahk` existed and were registered but had never been run before 2026-09-29.

**Bravo facts (verified on the Aug 2026 pull):**
- Store credits and gift cards are company-wide — every store's file lists the same cards. Attribution is by ISSUING store.
- Layaway credit (money paid on expired layaways) is per store.
- Journal store prefixes: VP4=CUL, VA5=HAR, VA1=LEX, ROA=ROA, VAP=WAY. `STA` = closed Staunton store (legacy gift cards).
- Only Roanoke issues true "store credit"; the other stores put store credit on a gift card.

## Formatter
`Valley Pawn OS/bin/gift_credit_monthly.py <YYYY-MM> <bravo output dir> <out dir>` — deterministic. Exit 0 = publish stdout verbatim; exit 2 = HOLD.txt, publish nothing. Reconciliation checks (all must pass): detail rows = report totals; balance report = journal ending; journal begin + activity = ending; by-store sum = company total; as-of date and journal range match the month; company-wide sections identical across all 5 store files.

Outputs per month in `out/<YYYY-MM>/`: `slack_post.txt`, `gift_credit_<YYYY-MM>.json`, `gift_credit_<YYYY-MM>.xlsx` (customer names — internal only; archived to Drive 08 Reports & Analysis/Gift Card & Store Credit).

## Publication
Scheduled task `monthly-gift-card-store-credit` — 2nd of month 2:30 AM, Type A (one trigger). Posts to #company-performance (C0B26GD8D2R) and DMs the same text to Preston Peters (U03BWMEM9GR, per Joshua 9/29), marker `Gift Cards & Store Credit —`.

## August 2026 (first run, 2026-09-29) — all 26 checks passed
Company outstanding $25,919 (gift cards $4,106.69 · store credit $675.64 · layaway credit $21,136.68), up from $25,135 on Aug 1. Cross-checked against the End-of-Month report (CUL Gift Card Sales $229.80, Layaway Expirations to Credit $185.30 — match).
