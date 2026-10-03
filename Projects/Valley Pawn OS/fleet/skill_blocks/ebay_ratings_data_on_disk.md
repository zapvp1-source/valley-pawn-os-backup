# STEP 1 IS DONE BY THE MAC — READ THE FILE (added 2026-10-02, overrides Step 1)

Do NOT run `ebay_ratings_headless.py` — it needs `~/.vp_secrets`, which this session cannot reach (that is
why the 2026-10-01 run failed). A native agent (`com.valleypawn.ebay-ratings-pull`, 1st of month 09:45)
runs it on the Mac 15 minutes before this task and writes:
`/Users/joshuadavis/Documents/Claude/Projects/eBay/ebay-ratings-sweep-<YYYY-MM>.md`
Read that file with the Read tool and continue at Step 2. If it is missing or older than today, write one
FAILURE_LEDGER row and stop — never guess numbers.

**Post format (locked 2026-10-02 to the 2026-09-01 post):** title line "eBay Store Ratings Sweep — all 5
accounts — <Month YYYY>", then "Ranked by 12-month positive %:", one numbered line per store
`N. Store (username) — Score X | 12-mo positive: Y% | 1-mo: a/b/c · 6-mo: … · 12-mo: … | TRS: …`, then a
Seller Standards line, a "Vs. <prior month> sweep:" line, and a short "Bottom line:" bullet list.
