# eBay Desk — build status (controlled build; nothing live)

Rule (Joshua 11/17): no live action or transaction in eBay or Bravo until tested and approved. A mistake here distracts all 5 stores.

## Built 2026-11-18 — Stage 1 logic, offline
- `desk_core.py` — reads saved eBay order files and Bravo's daily sold export (`sold-discount-detail` CSV). Produces: the "Ring these sales" list per store, the 24-hour not-rung check, and a double-sell list (plan only). It imports no network library and no eBay token; a test enforces that.
- `test_desk.py` — 17 tests, all pass (`python3 test_desk.py`). Covered: cancelled and unpaid orders skipped; multi-item orders; price x quantity; Bravo number from SKU or title; model numbers like (A2482), (DCD771), (2236) never treated as Bravo numbers; re-pulling an order never duplicates it or un-marks a rung sale; an old Bravo sale of the same item number does not count as rung; double-sell list skips items that sold on eBay.
- `fixtures/` — made-up orders and a made-up Bravo export. No customer data.

## Gates before anything touches eBay or Bravo (in order; each needs Joshua's OK)
1. Read-only shadow: pull real orders (GetOrders is a read) for 7 days into `out/`, post nothing, compare the not-rung list against what stores actually rang. Target: zero false "not rung".
2. Culpeper only: show the store the Ring list for 1 week. Still no eBay writes.
3. All 5 stores on the Ring list.
4. Double-sell guard goes from plan to ending listings: Culpeper first, max 3 per day, every one logged and reversible (relist).
5. List-an-item page: one test listing per store, then Culpeper for 2 weeks, then all.
6. Cutover and removal of Bravo's eBay access only after the old Bravo-made listings have run off.

## Not built yet
Order puller (read-only), the store page, list-an-item, returns.

## Gate 1 result — read-only shadow, 2026-11-18 (Joshua OK'd 11/18; "do not post anything in eBay or Bravo")
Run: `Valley Pawn OS/bin/ebay_desk_shadow.py 21` via host queue (only eBay call: GetOrders). Output: `out/shadow_2026-11-18_*.json/.csv`. 18 tests pass.
21 days, 5 stores: 90 sold lines, $18,274.
- 35 lines carried a Bravo item number: 34 found rung in Bravo (29 same or next day, 5 late by 2-8 days, all but one Roanoke), 1 not rung (Lexington, Canon EOS Rebel T6 VA1058519, $299.99, paid 11/3).
- 55 lines (61%) have NO Bravo number on eBay (title cleaned, SKU empty): Culpeper 28 of 30, Waynesboro 13 of 19, Harrisonburg 7 of 8, Lexington 7 of 8, Roanoke 0 of 25. The desk cannot tell a store which item to ring for these, and nobody can check they were rung.
- 2 rung lines differ in price by more than $1 (Roanoke: eBay $197.99 vs Bravo -$202.99 lower; $199.99 vs -$10.06).
Gate 1 verdict: the puller and the rung check work. NOT ready for gate 2 until the missing-number gap is closed.
Next, still read-only: match the 55 by description + price + date against Bravo's sold export. The lasting fix is writing the Bravo number into each live listing's SKU (engine/sku_link.py, buyer-invisible) — that is an eBay write and needs Joshua's OK.

## Design decisions from Joshua, 2026-11-18 (eBay project chat). Design only; nothing built or live from these.
Full text: Claude project doc `claude/ebay-desk-design-v2-2026-11-18.md`. The gates above still govern every step.
- Desk also takes listing requests: store enters Bravo item # + photos; desk builds, prices and sets shipping; price floor = cost + fees + label + packing.
- One shipping rule: free on small/light with label built into price; calculated (buyer pays) on heavy/bulky. Single-item minimum $40 (Joshua has not confirmed $40 vs $50).
- Sold in Bravo -> down on eBay in near real time. Three layers: eBay tag/bin/hold; short-cycle Bravo sold sweep; "Sold in store" button. Joshua: OK to pay for an extra Bravo admin key on the server for the sweep. He has one admin key on this Mac that reaches all 5 stores. Sweep needs its own Bravo session (second Windows VM) so it never collides with the existing Bravo jobs. Cycle time not measured yet.
- Server: this Mac Studio becomes the server when the new Mac Studio arrives in December; desk hosted here behind a secure tunnel; new Mac is Joshua's daily machine. Recommended: fleet stays on this Mac, only Joshua's working setup moves.
- Store PCs: nothing installed; Intune pushes the desk as an Edge web app. Enrollment of store PCs not yet confirmed.
- Emailed Preston 11/18 11:45 AM (Gmail thread 1a1ef8bc86f8195e) the 12-month profit numbers and the four proposed changes, asking for store-side downsides. Reply pending.
- 12-month eBay ledger actuals (Nov 2025 - Oct 2026, Quickbooks Set UP/ebay-finances-*.csv): net sales $289,081; fees $44,718 (15.5%, incl. $3,036 Below Standard surcharge); other eBay charges $1,297; labels $22,637 (7.8%); refunds $25,867; 1,944 orders.
