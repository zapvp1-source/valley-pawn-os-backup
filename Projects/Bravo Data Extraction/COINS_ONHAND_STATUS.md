# Coins & Bullion On-Hand — pipeline cell `coins-onhand` (STATUS)

Created 2026-09-05 after Joshua asked "do we have any gold coins for sale, what's the cost and price?"
and nothing in the pipeline could answer it.

## Why it did not exist
- `active-inv-details` (all on-shelf items) cannot complete on any store — DevExpress virtualiser
  stops yielding rows on 2,000+ row grids; the 2026-08-03 truncation guard now fails it loudly
  (BRAVO_KNOWN_ISSUES.md 2026-08-03 PM).
- Only category-filtered saved reports exist for jewelry (`Claude Jewelry Audit - *`), none for coins.
- eBay store: 428 live listings, zero gold coins (checked Website/shop-build/items.json 2026-09-05).

## What was built (additive, Rule #4)
| Piece | State |
|---|---|
| `reports/CoinsOnHand.ahk` — handler `PullCoinsOnHand`, cell name `coins-onhand` | WRITTEN. Clone of ActiveInvDetails + BoxReportName verification guard (from AgedJewelrySales step 3b) + verified-empty-grid = legitimate 0 rows. Output `output/<date>_<STORE>_coins-onhand.csv`, default column layout (Number, Status, Category, Description, Cost, Price, Last Sold Price, Date). |
| `bravo_watcher.ahk` | 2 lines added (include + registration). Backup `bravo_watcher.ahk.bak-pre-coins-onhand-2026-09-05`. Watcher restarted 12:22 via `_restart_watcher_v2.ps1` → PASS (PID 5576). Guard flag acquired/released around it; check was CLEAR. |
| Saved report **"Claude Coins On-Hand"** in Bravo | **NOT YET CREATED — blocker.** Needs a Bravo screen session (Parallels). Computer-use access request timed out twice (Joshua away). |
| Scheduled task (weekly trigger drop) | NOT YET — create only after the saved report exists and one manual trigger succeeds. |

## Saved report spec (Inventory sidebar → Custom Reports → Custom Inventory Report Generator)
- Name: `Claude Coins On-Hand` (exact — the handler verifies BoxReportName contains it)
- Criteria: Category IN {Gold Coin, Silver Coin, Coin, Gold Bullion, Silver Bullion}
  (also consider "Collection" — coin collections were logged there at WAY). Status = in stock / on shelf.
- Columns: default layout is fine (has Cost + Price). "Is Shared" = yes if offered; otherwise create in all 5 stores (saved reports have historically been per-store — jewelry v2 keeps a per-store GUID cache for that reason).
- Expected size: a few dozen rows per store → well under the ~270-row virtualiser window.

## Next steps (in order)
1. With Joshua present: `_bravo_foreground_guard.sh check` → `acquire coins-onhand-build` → request Parallels access → create the saved report (CUL first) → test trigger:
   `{"id":"coins-onhand-smoke-CUL-<ts>","requested_at":"...","reports":[{"name":"coins-onhand","stores":["CUL"],"date":"YYYY-MM-DD"}]}`
   → confirm CSV rows match the grid's "Row X of TOTAL" → repeat report creation for the other stores if not shared → `release`.
2. Register weekly scheduled task `weekly-coins-onhand` (Type A trigger drop). Spacing rule: ≥45–60 min from other Type A/C fire times; candidate Wednesday 5:35 AM ET is NOT free (bravo-health-watchdog 5:00, prestaging 6:34, morning pull 6:53) — use ~12:30 PM Tue (midday window was CLEAR on 2026-09-05, next Type C is 5 PM) after re-checking `grep -l 'Bravo Data Extraction' ~/Documents/Claude/Scheduled/*/SKILL.md` cron lines.
3. Reader: post to Slack (plain language) a per-store table of coins/bullion with cost, price, days on shelf; withhold the whole post if any store cell errored (Rule 18).

## Interim answer given to Joshua 2026-09-05 (from intake-detail / sold-discount-detail / items-to-price CSVs)
Gold coin/bullion intake last ~60 days: CUL 1909 Indian $5 ($300, 7/1 buy); CUL 1908 $2.50 Quarter Eagle ($225 loan 7/7); CUL 2019 1/10 oz Eagle ($200 loan 7/7); WAY 1920 Mexico 5 Pesos ($15.50 buy 8/17, still unpriced 9/5); HAR 1905 Liberty $10 ($250 buy 8/25); CUL 2003 Gold Eagle ($225 buy 9/3); CUL Egypt 1/200th scarab ($25 loan 9/2); ROA Scottsdale 1/100th bullion ($20 loan 9/4).
Sold: NGC 2020 Gold Eagle MS69 $350→$550→$545 (8/25); Karatbars 2.5g $410→$450→$425 (9/4); two 1/200th gold coins $25→$60→$50 (9/4); ROA Goldbacks $2–5→$5–25.
