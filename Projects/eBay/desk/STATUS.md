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

## 2026-11-19 — gap closed (read-only), eBay project chat
- New `match_unnumbered.py` (read-only, no network): matches eBay lines with no Bravo number to Bravo's sold export by store + date + price + description. On the 11/18 shadow: 55 unnumbered lines -> 50 match, 5 probable (two Culpeper Switch 2 bundles = VP4033066 and VP4033693, both rung 10/29; three PS5 consoles). Output `out/unnumbered_match_2026-11-18_1533.csv`.
- Result: 89 of 90 eBay sales over 21 days were rung in Bravo. Only miss: Lexington, Canon EOS Rebel T6, VA1058519, $299.99, paid 11/3 — still not in any Bravo sold export as of the 11/18 export.
- Why numbers are missing: the unnumbered sales are mostly newer listings (item IDs 9200…) that carry no code in title or SKU. `sku_link.py all` dry run 11/19: 380 active listings, 255 linkable (Culpeper 125, Roanoke 89, Waynesboro 24, Harrisonburg 10, Lexington 7), 125 with no recoverable code. SKU write still needs Joshua's OK. The matcher covers the rest until desk-built listings carry the number from the start.
- Preston replied 11/18 3:12 PM: list direct to eBay ("easier than listing through Bravo"), keep eBay and Bravo synced. Joshua replied he'll work on it. Open item closed.
- Design v2 (project doc) adds buyer-message auto-replies as build step 2. Checked 11/18: existing Trading API tokens read messages on all 5 stores; replies via AddMemberMessageRTQ / AddMemberMessageAAQToPartner; no re-consent needed; eBay API license permits it (no training on buyer data). 168 buyer questions in 30 days, 51 showing unanswered.

## 2026-11-19 08:05 — Joshua: OK to write Bravo numbers into SKU (done); stores must NOT ring eBay sales — ringing has to be automatic
- `sku_link.py --apply` done 11/19, all 5 stores: 254 of 255 linkable listings now carry the Bravo number in SKU (Culpeper 125, Roanoke 88, Waynesboro 24, Harrisonburg 10, Lexington 7). Run IDs 20261119-130622/130648/130716/130826/131136/131609/1318xx-skulink in engine/ledger.jsonl; revert with `sku_link.py --revert <run_id> --apply`. One Harrisonburg retry succeeded. 1 left: Roanoke 307242627482 (eBay refuses revise while ending in <12 h / active offer) — re-run `sku_link.py Roanoke --apply` next day.
- NOTE: engine Lock lives at ~/ebay_engine.lock; when run from the Cowork device shell that resolves to the sandbox home, NOT the Mac's real home, so it does not guard against the Mac's nightly engine. Run applies from the host queue / native agent in future.
- 125 live listings still have no Bravo number anywhere (Culpeper 55, Waynesboro 41, Harrisonburg 13, Lexington 13, Roanoke 3). Next: match them to Bravo intake-detail by description + price (read-only), then write SKU.
- DESIGN CHANGE: "Ring these sales" is no longer a store task. The desk rings each eBay sale in Bravo itself (eBay tender, Bravo item number, sold price + shipping). Needs a new Bravo POS sale handler — no POS write handler exists today (existing writes: vendor receiving, scrap closeout, user termination). Must run in its own Bravo session (second admin key, second VM) so it never collides with the report pipeline. Gates: map the sale screen read-only → one test sale on a test item with Joshua watching → Culpeper only, capped, every ring logged and voidable → all 5. Stores see nothing to ring.

## 2026-11-19 08:30 — sync cadence (Joshua's proposal, agreed)
- eBay -> Bravo ringing: once a night after all 5 stores close, ~9:30-10 PM ET (before midnight so sales land on the day they were paid and month-end stays clean), plus a 5 AM catch-up for anything that failed or was paid late. Batch run on the dedicated Bravo session; no contention with daytime store work. To verify in the sale-screen mapping: whether Bravo's end-of-day/business-date close blocks after-hours sales.
- Store -> eBay takedown: every 10 minutes during store hours via the Bravo sold pull, plus the instant "Sold in store" button. Overnight none needed (stores closed).
- Daytime guard for items sold on eBay but not yet rung: eBay items live in the eBay bin, not the floor; the morning "Ship these" list has the store pull them. If the counter rings one anyway, the nightly run sees it already sold and puts it on the exception list.
- Nightly reconcile both ways after the ringing run.

## 2026-11-19 08:32 — sold-pull timing (measured from Bravo Data Extraction/results, 478 successful sold-discount-detail cells)
- Median 112 s per store (range 76–325 s). All 5 stores, last 7 daily runs: 8.5–14.5 min. So a store-by-store pull can't hit a 10-minute takedown cycle and would tie up the only Bravo session.
- Plan: one company-wide Bravo custom inventory report (filters Store=all, Status=SOLD, Status Date=today, eBay/For Sale Online items only) on the dedicated sweep session; expected ~2 min per pull, looped back to back -> takedown within ~5 min. Verify in mapping. Fallback: store-by-store loop on the dedicated session (~10–15 min freshness) + "Sold in store" button.

## 2026-11-19 09:01 — Joshua: ALL items stay on the sales floor (eBay-bin / "eBay or floor, never both" rejected). Standard: must match Bravo's integration with no gaps, or don't replace it.
- Consequence: with items on the floor, both directions need a live link to Bravo (counter sale -> end eBay listing in seconds; eBay sale -> Bravo shows sold so the counter can't sell it). Screen-driven polling (minutes late, breaks on Bravo updates) does not meet the standard. Nightly ringing does not meet it either (item stays sellable in Bravo all day).
- Decision framework given to Joshua: replacing Bravo's listing (dropping the 5%) is GO only if Bravo provides a real data connection (sale event/feed out, sale/hold in). Otherwise listing stays in Bravo and the desk does only the parts with no Bravo timing dependency: shipping rule, price floor, $40 minimum, buyer-message auto-replies, SKU link, daily rung-check.
- Pending Joshua: OK to draft the Bravo email (data connection, what the eBay module does on in-store sale and on eBay sale, extra key). The every-10-min sweep and nightly-ring-only designs in the project doc are superseded pending Bravo's answer.

## 2026-11-19 09:05–09:20 — Joshua: continue the build and test now on this Mac; extra Bravo key waits for the new Mac Studio
Built (all offline-by-construction, plan-only; nothing sends):
- `desk_sync.py` — takedown_plan (counter sale -> listings to end; 2-day window; skips eBay sales and already-ended; >10 in one run halts and ends nothing), ring_plan (ring / verified / recheck / exception, keyed store|line so nothing rings twice; counter-sold-first is an exception), classify_message + render_reply, shipping_mode, price_floor, listing_gate ($40 single minimum, restricted items, floor). `test_sync.py` 21 tests pass; `test_desk.py` 18 pass.
- `sync_shadow.py` — read-only rehearsal of both directions (GetMyeBaySelling + GetOrders + Bravo sold CSVs). `messages_shadow.py` — read-only classification of real buyer messages (GetMemberMessages).
Test results, live data, 11/19:
- eBay side is fast: all 5 stores' live listings 4.1 s, 60 days of orders 5.4 s.
- Takedown rehearsal: 0 to end right now. Stale audit: 1 live listing Bravo shows sold — Harrisonburg 800232060996 VA5019380 Nintendo Switch OLED, Bravo sold 9/24 $229.99 (either never taken down or returned and relisted; store to confirm).
- Ring rehearsal, last 3 days: 11 paid lines -> 3 already in Bravo, 2 to ring (Roanoke ROA012343 $39.99, ROA012530 $209.99, paid last night), 6 with no Bravo number (5 Culpeper, 1 Harrisonburg: sold before the 11/19 SKU write or among the 125 unnumbered).
- Same-day Bravo sold pull (trigger ebaydesk-sameday-sold-20261119T1407, existing sold-discount-detail cell, date=today): works, but an EMPTY store takes 5.5 min (CUL 327 s, waits out the grid timeout before accepting 0 rows) -> ~25 min for 5 quiet stores. The existing handler cannot serve the takedown loop. Needs a NEW dedicated handler (additive): one company-wide saved report, sold today, fast empty detection. Same-day header-only CSVs from this test must be moved out of output/ (tomorrow's morning pull overwrites them anyway).
- Buyer messages, 167 real questions in 30 days: first-draft rules auto-answered 7 and ALL 7 were wrong (offers with dollar amounts, order problems). Rules tightened; now 0 of 167 auto-send. Mix: offers/haggling 43 (26%), item-specific 69, condition 18, order 16, thanks/no reply needed 15, photo/video requests 4, contact 2. Of the 51 "unanswered": 18 offers, 9 thanks (no reply needed), 24 real questions. Conclusion: fixed-template auto-send is worth almost nothing on real traffic. Value is (a) item-specific replies drafted from the listing for one-tap store approval, (b) a standing reply to price offers if Joshua sets one, (c) the 24-hour unanswered flag.
Next (no approval needed): dedicated Bravo sold-today handler (new saved report + new cell, off-hours test); match the 125 unnumbered listings to Bravo; read-only map of Bravo's sale screen. Needs Joshua: wording/OK for a standing price-offer reply; the test sale + void.

## 2026-11-19 09:47 — same-day sold pull test finished (trigger ebaydesk-sameday-sold-20261119T1407, 09:07–09:41, status partial)
- CUL 327 s / 0 rows, HAR 324 s / 0, LEX 337 s / 0, ROA 325 s / 0 (all success, stores had no sales yet). WAY error after 647 s: "Could not select 'Claude Sold Inv Details'" (saved-report select failed); handler returned Bravo to the Dashboard cleanly (09:40:51), queue idle after. Total 34 min for 5 quiet stores.
- Confirms: the existing sold-discount-detail handler is not usable for the takedown loop. Dedicated company-wide sold-today handler required.
- The four header-only same-day CSVs were moved out of Bravo Data Extraction/output/ to eBay/desk/out/sameday_test/ so the morning jobs never see a partial day. No WAY file was written.

## 2026-11-19 10:05–10:50 — Bravo-side build + live timing (Joshua: "go")
- NEW handler `Bravo Data Extraction/reports/SoldTodayFast.ahk` (additive clone of SoldDiscountDetail; own names; output *_sold-today-fast.csv; empty decided at 45 s when the report surface is up — 384 logged valid renders took 0–22 s, p99 13 s). Registered additively in bravo_watcher.ahk (2 added lines; backup bravo_watcher.ahk.bak-pre-sold-today-fast-20261119). Validated + watcher restarted via host queue job z_ebaydesk_watcher_validate_restart_20261119 (rc=0, 10:20).
- Live test ebaydesk-soldtodayfast-20261119T1521 (10:21–10:48, 27 min): ROA success 229 s (1 row: ROA012343, last night's eBay sale, rung this morning), WAY success 368 s (empty decided at 49 s — the fast cut works), CUL / LEX error (Inventory > Custom Reports not found; Bravo UIA timeouts 0x80131505), HAR error (store switch stalled). Bravo was sluggish all morning, partly after the failed active-inv attempt.
- Where the time goes per store (successful cells): store switch via Lock Session 1–3 min, report setup ~30 s, grid ≤ 50 s, exit back to Dashboard ~1–1.5 min. Floor ≈ 3–6 min per store in daytime → 15–30 min for 5 stores, with ~40–60% daytime cell failure today. CONCLUSION: a per-store screen loop cannot deliver a 5-minute takedown, with or without a second Bravo key. Only two things can: (a) one company-wide report (no store switching) if Bravo's Store criterion allows it — untested, needs a new saved report built in the Bravo UI; (b) a real data feed from Bravo (their hosted SSRS report server already exports CSV by URL at ssrs.bravoapplication.com:9176 behind a Bravo-app-issued session; ask Bravo for service access).
- active-inv-details CUL (ebaydesk-activeinv-CUL-20261119T1506): failed, grid did not render in 120 s (CUL inventory too large) — same failure as every prior run since May. Not usable.
- 125 unnumbered live listings: on-disk Bravo exports match only 4 (they were listed Aug–Nov; exports on disk cover aged/unpriced items). Needs a small "listed online" inventory report.
- Test CSVs moved to eBay/desk/out/sameday_test/. Guard CLEAR at 10:50.

## 2026-11-19 12:00 — Joshua: risk accepted. "If the odds are 1 double sale in 5 years we are ok."
- DECISION: store-by-store takedown loop on its own Bravo session (extra key, new Mac Studio in December) is the design. Measured today 15–30 min per 5-store pass -> roughly one double sale every 2.5–5 years. "Sold in store" button + nightly two-way reconcile stay as backstops. Company-wide one-pull report (tonight's 9:30 PM build) is a speed-up, not a requirement.
- Build now on this Mac (current key, after hours / off the morning cluster): order feed, takedown executor (eBay EndItem, Culpeper first, capped), ring handler (map sale screen read-only -> one test sale + void with Joshua -> Culpeper capped -> all 5), store page. Cut over to the dedicated session when the new Mac Studio and extra key arrive.

## 2026-11-21 09:55 — Joshua: build the Bravo saved reports without screen control
- Path found: MobileEventsGoldOff.ahk (crbuild mode, 11/20) already builds + saves a NEW shared saved Custom Report inside the VM via UIA, no Mac screen control (built "Claude Loan Reminders" 11/20 19:44, SAVED+LISTED). Plan: clone it as InvReportBuild.ahk (Inventory > Custom Reports; invprobe read-only first, then build "Claude eBay Sold Today All" and "Claude eBay Listed"), launched by a cloned bin/inv_report_build.sh + _run_invreport.ps1.
- Blocked: adding inv_report_build.sh to fleet/host_queue_allowlist.txt (needed for the host queue to launch it) was refused by the session's safety check. Nothing was written. Needs Joshua's explicit OK to add one line to the allowlist (or to run it another approved way).

## 2026-11-21 19:40–20:58 — Bravo reports built without screen control (Joshua approved 11/21 09:57: add the job + the two reports)
- New job: Bravo Data Extraction/InvReportBuild.ahk (clone of MobileEventsGoldOff.ahk; modes invprobe / invdry / invbuild), launcher _run_invreport.ps1, Valley Pawn OS/bin/inv_report_build.sh; inv_report_build.sh added to fleet/host_queue_allowlist.txt (backup host_queue_allowlist.txt.bak-pre-invreport-20261121).
- SAVED + LISTED in Bravo (Shared Company-Wide, built at CUL 20:13 / 20:15):
  A "Claude eBay Sold Today All": layout "Sold inv detail", Status = SOLD, Status Date range, Store = All stores.
  B "Claude eBay Listed": layout "Inv item detailed", Status = INVENTORY, Web Platform = EBAY (per store; no Store criterion).
- New pipeline cells (additive, watcher validated + restarted twice): sold-today-all (reports/SoldTodayAll.ahk; trigger store "ALL" = no store switch) and ebay-listed (reports/EbayListed.ahk). Backups bravo_watcher.ahk.bak-pre-sold-today-all-20261121, .bak-pre-ebay-listed-20261121.
- TIMING sold-today-all, 3 back-to-back runs: 94 s, 88 s, 88 s. 92 rows, all dated 11/21, from ALL 5 stores (ROA 21, HAR 19, WAY 19, CUL 18, LEX 13, +2 SKU items). => takedown pass ≈ 1.5 min, no store switching. Double-sell odds at a ~2-minute loop: roughly once in 15+ years.
- ebay-listed per store: CUL 194 (2nd try; 1st hit the Done-loop), WAY 82, HAR 38, LEX 43, ROA 110 = 467 items Bravo has marked EBAY; 104–130 s per store.
- SKU link: 72 unnumbered live listings matched to Bravo's eBay-listed items and written (run 20261122-0152xx/015605-skulink-matched, all ok) + 7 new Roanoke title codes (sku_link). Now 323 of 381 live listings carry the Bravo number (85%); 58 left with no confident match (CUL 35, WAY 16, HAR 5, LEX 2).
- Pull CSVs moved to eBay/desk/out/bravo_pulls/ (out of Bravo output/).

## 2026-11-21 23:40 — watch-only takedown loop installed (Joshua "ok")
- eBay/desk/takedown_watch.py + Valley Pawn OS/bin/ebay_takedown_watch.sh + fleet/com.valleypawn.ebay-takedown-watch.plist (bootstrapped 23:48; native_live marker set). Every 20 min at :07/:27/:47, 10:00–17:59, open days only (Sunday none). Skips when Bravo is busy, a trigger is waiting or the foreground guard is held; never self-heals Bravo; takes its trigger back if not claimed in 6 min.
- WATCH ONLY: logs to eBay/desk/out/takedown_watch.jsonl (would-end listings, first-seen time, and when a listing later disappears = today's manual takedown lag). No eBay or Bravo writes. Dry run on 11/21 data: 92 sold rows, 379 live (318 numbered), 0 would end.
- First live rounds: Monday 11/23 10:07. Review after 3–5 open days: every would-end must be a real counter sale of a live listing; then ask Joshua for the OK to end for real (Culpeper first, cap 3/day).
- Still open with Joshua: OK to end listings for real; test sale + void; standing reply to price offers; Slack to Lexington (Canon VA1058519) and Harrisonburg (Switch VA5019380); what to do with the 58 unnumbered listings.
