# Bravo Warehouse — STATUS (resume here)

Goal (Joshua, 2026-11-27): ALL Bravo data in one queryable place, deep history first, daily refresh where easy.
Tie buys/loans to sold and aged inventory: time to sell, carrying cost, profit of slow movers. Plan: PLAN.md.

## Built 2026-11-27
- bin/build_warehouse.py — READ ONLY on the pipeline; full rebuild (~5 s) -> bravo_warehouse.sqlite + COVERAGE.md.
  Run from a device-bridge session: `python3 bin/build_warehouse.py --tmp $HOME/whtmp` (SQLite cannot be written
  directly on the mounted folder; the script builds in --tmp and copies the finished file in). On the host no flag needed.
- Tables: inventory_snapshot, item_sales, buy_items, intake_items, loan_items, layaway_snapshot, unpriced_snapshot,
  source_files. Views: v_inventory_latest, v_sales_with_age, v_coverage, v_sales_coverage_by_month.
- Fixed Valley Pawn OS/bin/instock_merge.py (backup .bak-pre-asof-fix-20261127): As Of.txt lock no longer blocks the
  Drive publish. 11/26 list published.

## Backfill queue (existing cells only; one month, all stores, per trigger; Sundays / idle slots)
Drop as host-queue jobs: `bash ".../Valley Pawn OS/bin/bravo_pull.sh" <cell> <from..to> <STORES> <id>`
1. sold-discount-detail: 2026-05-18..05-31 (LEX smoke dropped 11/27 15:22), 2026-06, 2026-07, 2026-08-01..08-11
2. buys-from-public: 2026-05 .. 2026-11 monthly (CUL has to 5/13)
3. loan-portfolio-2026: 2023-01 .. now, monthly by create date (rows cap: keep <= 1 month)
4. sold-discount-detail older: 2025-04 backwards until empty
5. buys-from-public older: 2024-04 backwards
After each batch: rebuild, read COVERAGE.md.

## Next builds
- "Claude Item Master" layout + saved report (Inventory > Custom Reports) via InvReportBuild.ahk pattern. Probe read-only
  first whether a column layout can be created by script. Columns in PLAN.md Step 3. Additive only.
- Prove LoanJournal / LoanDisposition / LoanHistory / LayawayJournal / SoldInventory / Transfers / CostAdjustment /
  LostStolenOrDamaged handlers (one store, one month), then backfill.
- EOM validation table (parse end-of-month.csv; tie cost of sales, revenue, inventory base, loan base per store-month).
- Native nightly rebuild agent (needs build_warehouse.py on fleet/host_queue_allowlist.txt — asked Joshua 11/27).

## Known quirks
- item_sales history file (Deep KPI, 5/2025-5/2026) is used only for days the daily feed does not cover.
- Only items present in a nightly snapshot (since 11/24) have since_date; older sold items need the Item Master pull.
- pm-loan-growth rows are jewelry/metal loans only (period snapshots), not the whole loan book.
- Rocket Pawn (FL) is not in any pipeline; asked Joshua 11/27.

## 2026-11-27 later
- NEW cell `sold-history` (Bravo Data Extraction/reports/SoldHistoryAll.ahk; watcher backup .bak-pre-sold-history-20261127):
  sold items for a date range by whole-grid copy, count-checked. Proven LEX 5/18-5/31/2026: 152 of 152 in 68 s.
  The older sold-discount-detail walk came back short on the same window (135 of 152) — do not use it for backfill.
- Use sold-history for ALL sold backfill. Never pull overlapping sold-history windows for a store (the loader would
  count those days twice). Keep each window under 5000 rows (one month per store is ~300-800).
- Dropped 15:40: 2026-06, 2026-07, 2026-08-01..11 (all stores) and 2026-05-18..31 (CUL,HAR,ROA,WAY).
- Clone this handler for buys and loans history (BuysFromPublic / LoanPortfolio2026 saved reports) next.
- Scheduling from a cloud session: send_later is refused (session is bound to the Mac). Waiting inside device_bash
  does not work (sleep returns at once); use a background `sleep` in the cloud shell.

## 2026-11-27 evening
- 2026 sold gap (5/18-8/11) filled, all stores, every pull matched Bravo's count.
- Joshua: allow-list OK; Rocket Pawn is NOT on Bravo yet (out of scope).
- INSTALLED native agent com.valleypawn.wh-backfill (Valley Pawn OS/bin/wh_backfill.sh, allowlist backup
  .bak-pre-wh-backfill-20261127). Sundays 9:20, 10:20, 11:20 AM, 3:20, 6:30, 7:30, 8:30, 9:30 PM: 4 windows each from
  backfill_queue.txt. Daily 3:05 AM: rebuild only. Pause: create fleet/state/wh-backfill/PAUSED. State: fleet/state/wh-backfill/.
  First Sunday run 11/29. Verify Monday: done markers, COVERAGE.md, ~/Library/Logs/valleypawn/wh-backfill.log.
- ACCURACY LIMIT: vs End of Month 8/1-8/27/2026 the item_sales cost is 87-92% of "Sales (Cost of Sales)" per store
  (CUL 18,585 vs 21,390; HAR 16,574 vs 18,243; LEX 10,911 vs 12,257; ROA 9,715 vs 11,072; WAY 16,337 vs 18,740).
  Cause (likely, partly verified): stock-number items sold repeatedly appear once, with their latest sale only
  (about 8% of rows/cost in the daily feed are repeat numbers). One-of-a-kind items are complete.
  => item_sales history is NOT total sales. NEXT BUILD: prove the built-in Sold Inventory report (reports/SoldInventory.ahk,
  cell sold-inventory) one store one month, tie it to End of Month, then backfill it as the sales ledger.
- Then: clone SoldHistoryAll.ahk for buys (saved report used by BuysFromPublic) and loans (Claude Loan Portfolio 2026),
  add their windows to backfill_queue.txt; then the Item Master layout probe.

## 2026-11-27 ~5:10 PM — CORRECTION + ledger proven (supersedes the "ACCURACY LIMIT" numbers above)
- The 87-92% figure above was WRONG: it added the DAY pair and the MONTH pair on the End of Month "Sales (Cost of
  Sales)" line. In that file the first qty/amount pair is the report's last DAY, the second is the MONTH.
  Correct: item_sales (item report) is 92-98% of month cost of sales (CUL 92.8, HAR 93.7, LEX 98.5, ROA 94.4, WAY 91.6).
- SALES LEDGER PROVEN: cell sold-inventory (existing handler, built-in Sold Inventory report) LEX 8/1-8/27/2026 =
  227 lines, cost 11,028.32 = EOM Sales (Cost of Sales) 11,081.98 - Returns (Cost of Sales) 53.66. Exact.
  EOM COGS 13,120.32 = 11,081.98 - 53.66 + Refined (Cost of Sales) 2,092.00. Loader table sales_ledger; ledger_files
  records each file's own Total check (ties) and whether it was used (longest window wins, overlaps skipped).
- NEW cells loans-written / buys-written (reports/TicketHistory.ahk, FwbRun, FDP layout; watcher restarted ~4:50 PM).
  LEX Aug 2026: loans 152 rows / 108 tickets (97 tickets through 8/27 = EOM New Loans 97; amount 15,162 vs EOM 14,612,
  550 apart = the one renewal). Buys 212 rows; 94 tickets through 8/27 vs EOM 89 buys (1 void; rest not yet explained
  - OPEN: reconcile buys count/amount 17,197 vs 16,289). Loader table ticket_items.
- backfill_queue.txt rebuilt: Nov 2026 -> Jan 2021, per month: sold-inventory, loans-written, buys-written; then older
  sold-history. Sunday slots now 6 windows. First live agent-script run dropped 5:05 PM (4 windows).
- Ticket dispositions change over time: re-pull the trailing 6 months of loans-written quarterly (not yet scheduled).
- STILL TO BUILD: Item Master layout (item -> ticket link, date to inventory); EOM monthly tie-out table for every
  store-month; journals (loan payments/interest, layaway), transfers, cost adjustments, shrinkage.

## Update 2026-11-27 ~7:10 PM ET

- **End of Month check is in the warehouse.** `build_warehouse.py` now parses every `*_end-of-month.xlsx/csv` in the pipeline output (cached in `cache/eom_cache.json`) into `eom_report`; view `v_eom_month` = one row per store and full calendar month, view `v_tieout_sales` = EOM cost of sales less returns vs the sales ledger. COVERAGE.md lists it. October 2026 ties to the penny at all five stores. Full-month EOM files on disk: 2024-07 to 2026-10 except 2024-10, 2024-11, 2025-09, 2025-10, 2026-08.
- EOM lines for 2024-10, 2024-11 and every month 2024-06 back to 2021-01 were added to `backfill_queue.txt`. NOT queued: 2025-09, 2025-10, 2026-08, because files named `<month end>_<STORE>_end-of-month.xlsx` already exist with a different (12 month or partial) window and other automations may read them. Needs a non-colliding output name before pulling.
- Buys check still open: LEX Aug 2026 EOM says Buys 89 tickets $16,289 (also "Expired Buys / Trade-Ins" 90, $17,009); buys-written through 8/27 gave 94 tickets incl. 1 void, $17,197.
- **Item master layout is scriptable.** Read-only probes (`inv_report_build.sh WAY layprobe2|layprobe3`, output in `Bravo Data Extraction/output/inv_reports/WAY_layprobe*.txt/png`): right-click any grid header > "Show Column Chooser" opens a window named "Column Chooser" with a search box and 60 columns, each with a tick box (CheckEdit). "Hide Column Chooser" closes it. The "Layouts" label beside the grid has an Expander (chevron) to its right; that is where a layout is saved (layprobe3 records it). `LayShot()` takes full-resolution screenshots (the older MerShot only captures the top-left quarter at 200% scaling).
- Seen during the probe: seven stale hidden "Bravo is already running." OK boxes sit behind Bravo on the VM (left by relaunch attempts). Harmless, not touched.

## Update 2026-11-27 ~8:45 PM ET: item master built (the item to ticket link)

- **Created in Bravo (additive, both Shared Company-Wide):** grid layout "Claude Item Master" (31 columns, layout id c863a071-6b99-4df4-b430-c55e81c1d7ab) and saved Inventory custom report "Claude Item Master" (that layout, Status Date range, NO status criterion so every status returns). Built by `inv_report_build.sh WAY laybuild` then `itembuild` (modes added to `InvReportBuild.ahk`; `laydry`/`itemdry` are the no-save versions). Existing layout "Sold inv detail" re-checked afterwards: same id, same 8 columns.
- How the layout build works, for next time: open a saved report, right-click a header > Show Column Chooser, set each column through the chooser's search box (never by scrolling: rows recycle and clicks land on the wrong column), open the Layouts chevron (check its ToggleState, the panel element exists even when closed), type the name, sharing combo, press Save (not Update).
- **New cell `item-master`** (`reports/ItemMaster.ahk`, clone of SoldHistoryAll; watcher lines added, backup `bravo_watcher.ahk.bak-pre-item-master-20261127`). Window = Status Date range, per store. Raises the report's default 250 row cap to 5000 for the run (FwbSetMaxRows) and refuses a result of exactly 250 or >= 5000. Output `<from>_to_<to>_<STORE>_item-master.tsv` + `.meta`.
- **Proven:** LEX August 2026 = 556 rows (549 items), Bravo count matched. Statuses: SOLD 242, INVENTORY 134, SHRINK 52, REDEEMED 41, REFINED 37, DEFUNCT 36, LOAN 10, LAYAWAY 3, CUSTOMER ITEM 1. SHRINK 52 items / $868.11 equals End of Month shrinkage exactly. Each row has Source (BUY, PAWN, PURCHASE, SKU), Type (EXPIRED BUY, OUT OF PAWN, RETURN ...), Last Ticket Number (e.g. BT-VA1025530-01; drop the trailing -NN to match `ticket_items.ticket_no`), Date to Inventory, customer, metal weight and purity.
- **Warehouse:** table `item_master`, view `v_item_origin` (adds `ticket_no` and `days_in_inventory`). An item appears under its CURRENT status and status date, so re-pulling a window later can move items (e.g. INVENTORY becomes SOLD in a later month). When the same item shows in more than one file, the newest file is the truth; a `v_item_master_latest` view is still to build once more months are in.
- **Queue:** `item-master` now leads every month in `backfill_queue.txt` (Nov 2026 back to Jan 2021) and continues alone back to Jan 2016. 131 windows.
- **Agent:** `wh-backfill` also runs every night at 11:20 PM, 4 windows (after loan reminders 10:40 PM, before the 1:45 AM inventory pull). Sundays unchanged.
- Open: daily "status changed yesterday" item-master pull is not scheduled yet (add to the nightly slot once history is in); buys tie-out; money-trail reports; 2025-09, 2025-10, 2026-08 End of Month full-month files.

## Update 2026-11-27 ~10:40 PM ET: money trail first tests (LEX, October 2026, ids wh-test-<cell>-LEX-2026-10)

- `transfers`: works (5 rows, `2026-10-31_LEX_transfers.csv`).
- `loan-journal`, `loan-history`, `layaway-journal`: FAIL "Preview did not render within 60s". The diag dump still shows the Reports list, so either the tile/Ok click did not take or a month takes longer than 60 s to render. Next: clone each into a new handler (do not edit the originals) with a longer preview wait and a screenshot at the failure point, test on ONE day first, then a month.
- `loan-disposition`: reached the export dialog, "CSV file did not appear within 180s". Next: same clone approach, longer file wait; try a one-week window.
- `cost-adjustment`, `lost-stolen-or-damaged`: still queued behind the 10:40 PM loan reminders when this was written; check `results/`.
- Per-trigger logs: `Bravo Data Extraction/logs/wh-test-<cell>-LEX-2026-10.log`.
- Not yet verified: first nightly `wh-backfill` run at 11:20 PM (look for new markers in `Valley Pawn OS/fleet/state/wh-backfill/done/` and `~/Library/Logs/valleypawn/wh-backfill.log`).
