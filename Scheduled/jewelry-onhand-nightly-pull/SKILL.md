---
name: jewelry-onhand-nightly-pull
description: Nightly 8:30 PM (Mon-Sat) — THE single local jewelry count task: pull 5-store Bravo on-hand counts inside the after-close freeze window, read the PM count sheets from #end-of-day, and post the Expected/Counted/Variance table to #jewlery-counts.
model: claude-sonnet-5
---

THE single local nightly jewelry count task for Valley Pawn (consolidated 2026-08-14 at Joshua's direction: one local task, end to end — Bravo pull + sheet read + channel post. The old companion `jewelry-onhand-nightly-compare` and sold-based `jewelry-count-reconciliation` are disabled; cloud jewelry tasks deleted).

## STEP 0 — OPEN-STORES GATE. Do this before anything else.
Only run for stores that ACTUALLY TRADED TODAY. Get the real weekday first via `mcp__Control_your_Mac__osascript`: date '+%A %Y-%m-%d'.
- Sunday -> NOBODY OPEN. Skip the entire run silently. Correct no-op, not a failure.
- Wednesday -> ["CUL"] only.
- Mon, Tue, Thu, Fri, Sat -> ["CUL","HAR","LEX","ROA","WAY"]
"COMPLETE" means every OPEN store done — a Wednesday run covering only Culpeper is complete.

═══ RULE 0 — NEVER REQUEST FOLDER ACCESS ═══
Do NOT call `mcp__cowork__request_cowork_directory`, and do not use Read/Write/Edit for anything under /Users/joshuadavis/Documents/. You run unattended; the approval prompt times out and kills the run (happened 2026-08-10). Reach EVERY file via `mcp__Control_your_Mac__osascript` shell commands (cat, ls, printf, python3). osascript quirks: wrapper dies ~25s — never sleep >18s in one call, poll with repeated short calls; append `|| true` to commands whose last stage may exit non-zero.

WHY THE TIMING MATTERS: Bravo's jewelry report is a LIVE on-hand query (no as-of-date). The manager's sheet is a physical case count at 6 PM close. All 5 stores close 6:00 PM, reopen 10:00 AM — so 6 PM→10 AM is the freeze window. You fire at 8:30 PM inside it; that's what makes the numbers comparable. If you cannot run inside tonight's freeze window, do NOT pull; report the miss and stop.

## STEP 1 — Contention check + health gate (mandatory, never touch Bravo blind).
- Via osascript: ls -la "/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/triggers/claimed/" — anything claimed in the last ~30 min means Bravo is in use; wait and re-check up to 3 times at ~10 min intervals, then STOP and DM Joshua one plain line (D03BHQH5VGT).
- RUN the health gate (do not just read its status file): bash "/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/bravo_health_gate.sh" — exit 0 = PASS. It self-escalates (VM start, agent bounce, Bravo relaunch, VM restart). Poll with short calls. Only proceed on exit 0. (2026-08-11: a wedged LEX login screen caused 13 hours of failed retries; the gate turns that into a ~3-minute VM restart.)

## STEP 2 — Drop the trigger (via osascript printf).
Write /Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/triggers/jewelry-onhand-<YYYY-MM-DD>.json :
{"id":"jewelry-onhand-<YYYY-MM-DD>","requested_at":"<now ISO, -04:00 during EDT>","reports":[{"name":"jewelry-case-counts","stores":<OPEN STORES from STEP 0>,"date":"<YYYY-MM-DD>"}]}
Confirm within ~60s it moved to triggers/claimed/. If never claimed, the watcher may be down — DM Joshua one plain line and stop.

## STEP 3 — Monitor hands-off. CRITICAL.
Tail logs/jewelry-onhand-<YYYY-MM-DD>.log via osascript only. ~6-12 min per store. DO NOT click, scroll, or touch the Bravo window — not even a category that looks stuck. (2026-08-10: a manual click during the handler's own retry recorded Rings as 25 when the truth was 644 — clean-looking wrong number.) The handler has its own retry logic; let it work.

## STEP 4 — Verify completeness. ALL-OR-NOTHING.
When the log shows "Overall status", confirm results/<id>.result.json shows status success for every OPEN store and output/<YYYY-MM-DD>_<STORE>_jewelry-case-counts.csv exists with every row status=ok (strip UTF-8 BOM: python open(...,encoding='utf-8-sig')). EMPTY-CATEGORY RULE (learned 2026-08-14 — READ THIS, it will fire most nights): a category with genuinely ZERO items on hand renders no grid rows, so the handler cannot read a row total and records status=error, NOT 0 (deliberate no-false-zeros design). Confirmed empty as of 2026-08-14: HAR Charms, WAY Charms, LEX Brooches. Treat a Charms-or-Brooches error as 0 ONLY IF that same store+category was also 0/error in the most recent prior day CSV in output/. If the prior day had a POSITIVE count (e.g. ROA Charms 60, CUL Charms 44, CUL Brooches 28), an error is a REAL read failure — do not treat as 0, follow the failure path. An error in Rings, Bracelets, Pendants, Earrings, Chains, or Necklaces is ALWAYS a real failure regardless. When you treat an error as 0, say so in the run output and in the DM if you send one.

If ANY store is missing, stale, or non-ok (after applying the empty-category rule above): post NOTHING to the channel, DM Joshua ONE plain line that tonight's jewelry count didn't complete, put technical detail in your run output, stop.

## STEP 5 — Read tonight's PM count sheets (Chrome vision pass).
Managers post sheet photos to #end-of-day (C03C7HV8L48) ~6:15-8:15 PM. Slack's API cannot read image pixels — use claude-in-chrome (if screenshots time out or return 0x0, activate Chrome via osascript: tell application "Google Chrome" to activate). Open https://app.slack.com/client/T03BL4W1DCL/C03C7HV8L48 and for each OPEN store zoom into the "JEWELRY DAILY COUNT" photo (open the lightbox for rotated/small sheets — Roanoke's is usually rotated 90°). Use the PM COUNT column of the block whose handwritten DATE matches today — sheets stack several days per page; read the right block. Identify the store from the sheet's own printed header, not the poster. SUM-VERIFY every column against its written TOTALS line; if it disagrees you misread a digit — re-zoom (disambiguate via total-minus-other-categories). If a store's sheet isn't posted yet, wait 30 min once, then if still missing follow the failure path (no partial posts).

## STEP 6 — Build and post the table to #jewlery-counts (C0BM9NHGTT4). FORMAT SET BY JOSHUA 2026-08-14.
Category mapping (Jewelry Category Standard, Preston 2026-08-14 — the handler now pulls 8 Bravo categories per store): RINGS = Rings. BRACELETS = Bracelets. EARRINGS = Earrings. PENDANTS = Pendants + Charms + Brooches SUMMED. NECKLACES = Chains + Necklaces SUMMED. The CSV has 8 rows per store; verify all 8 status=ok in STEP 4.
Post ONE message: first line "Jewelry Count — <Weekday> <M/D> (expected = system on-hand, counted = PM count sheet)" then ONE markdown table, columns Store | Category | Expected | Counted | Variance. Expected = Bravo freeze-window on-hand. Counted = PM sheet. Variance = Counted - Expected, signed (+/-/0). One row per category per store plus a bolded Total row per store. Open stores only. NO commentary, NO reasons, NO emoji, nothing else. Joshua's words: "we care about what is expected at the end of the day which is the bravo report against the eod paperwork" — no sold/transfer math ever.

## STEP 7 — DM Joshua (D03BHQH5VGT) ONLY if something needs attention.
On a clean night (all variances small/expected-direction), no DM. DM one short plain-language note only if: (a) an anomalous OVER variance appears (Counted > Expected — the case cannot hold more than the system has; sharpest attention; known standing case: ROA pendants entered as Charms, ~+61), or (b) the run failed (one plain line, no technical detail). KNOWN SCOPE CAVEAT (until a Location-filtered "Claude Case Jewelry" report exists in Bravo): Bravo counts case+safe+back-stock+bins while the sheet counts the display case only, so negative variances (Counted < Expected) are expected scope noise, NOT loss — never call them loss. CUL runs ~-130 total nightly for this reason; stable night over night.

## STEP 8 — Log (osascript append, never the Edit tool).
Append a dated RUN RECORD to /Users/joshuadavis/Documents/Claude/Projects/Jewelry Count Reconciliation/STATUS.md: full per-store table, freeze-window confirmation for both sides, and whether any variance repeats night over night (repeating same store/category = process or data problem; one-night spike = likely miscount). Do not overstate confidence; a category swinging by hundreds overnight is a suspect read, not a business event.

Failure policy: exactly ONE plain-language Slack DM to Joshua (D03BHQH5VGT) — "tonight's jewelry count did not complete" — no error text, no paths, no next steps. All technical detail goes in the run output. Never post failures to any channel or employee.