# Yield by Asset Class — Run Log

Newest entries appended at the bottom by `yield-by-asset-class-monthly` (day 6, 2:00 PM).
Technical detail goes HERE, never to Slack (vp-operating-rules Rule 16).

---

## 2026-09-07 — initial build + hardening (manual, this is the baseline)

**Coverage:** 20 months, Jan 2025 – Aug 2026, all 5 stores + COMPANY (120 rows).

**Company results**

| Period | Loan | Inventory | Blended |
|---|---|---|---|
| FY2025 (12 mo) | 12.55% | 20.04% | 16.05% |
| 2026 YTD (Jan–Aug, 8 mo) | 12.24% | 21.92% | 17.05% |
| 2025 Jan–Aug (like-for-like) | 12.55% | 19.26% | 15.62% |

Year over year, like for like: blended **+1.43 pts**, entirely from inventory (19.26 → 21.92);
loan yield slipped 0.31 pts. Retail gross margin 51.1% → 54.3%. Layaway collection velocity
40.9% → 37.4% while the balance grew 21%.

**Resolver sources used:** pipeline=90, analytics-same=5, analytics-prior=5.
The 10 non-pipeline resolutions are August 2025 and August 2026 — see below.

**Harness:** 6/6 PASS.

**Root cause found and handled — the EOM filename collision.**
Bravo's EOM handler names output by END DATE only (`<END_DATE>_<STORE>_end-of-month.xlsx`).
`monthly-analytics-prestage` pulls SIX windows per store per month (same-month / YTD / trailing-12,
current and prior year) and every one ends on the same day. Six pulls, one filename; last writer
wins. Result: `2025-08-31_*` actually held 9/1/2024–8/31/2025 and `2026-08-31_*` held
9/1/2025–8/31/2026, all 5 stores — flows ~11x too large, balances still valid. 10 of 265 files
affected. This is a RACE, not a deterministic bug, so any month can lose.

**Both Augusts recovered with ZERO Bravo contact** from the range-stamped copies
`monthly-analytics/2026-08/same-month-current_*` (Aug 2026) and `.../same-month-prior_*` (Aug 2025).
Recovered Aug 2026 net revenue matched the Bonus Program's independently-derived August close to the
penny on all 5 stores (CUL 61,998.28 · HAR 54,413.07 · LEX 27,754.28 · ROA 48,167.81 · WAY 40,705.46)
— that cross-check is now check #2 in the harness.

**Hardening shipped (all additive, nothing existing modified):**
1. `eom_validate.py` — shared trust layer. Reads each file's own `Reporting Dates:` header; resolves
   the best trustworthy file per (store, month) through a 4-step fallback; refuses any file whose
   range is not exactly the month. Fast path reads the xlsx zip directly (~1 ms vs ~400 ms via
   openpyxl — the difference between a 3-second and a 2-minute run).
2. `eom_archive/` — range-stamped archive, `<START>_<END>_<STORE>.xlsx`. Collision-proof by
   construction, so no window can ever destroy another's data again. Backfilled 221 files from
   everything on disk; 0 unreadable.
3. `test_yield_by_asset_class.py` — 6-check regression harness gating every publish.
4. `render_yield_artifact.py` — regenerates the artifact's entire data blob from the CSV, so no
   figure on the published page is ever hand-typed or able to go stale.
5. `yield-by-asset-class-monthly` scheduled task (Type B, day 6, 2:00 PM, sonnet).

**Deliberately NOT changed** (Rule #4 — hardened infra): `EndOfMonth.ahk`, `OutputFilename()`,
`monthly-analytics-prestage`, `layaway-yield-weekly`, `store_kpis_compile.py`, `bonus_kpis_extract.py`.
The collision is made harmless rather than prevented, because preventing it means renaming outputs
that ~20 tasks depend on.

**Still open:** `layaway-yield-weekly` divides month-to-date collections by a full balance, so its
published % tracks the calendar rather than performance. Extraction verified correct (matched
`layaway_yield_compile.py` cell-for-cell, 2026-07-14, all 5 stores). Logged in the Open Items
Register for Joshua's call — not changed here.
