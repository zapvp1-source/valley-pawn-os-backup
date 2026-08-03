---
name: jewelry-count-reconciliation
description: Daily jewelry count reconciliation — pulls sold-jewelry counts from Bravo, reads manager AM/PM count sheets from #end-of-day, compares, posts results to #jewlery-counts
---

# Daily Jewelry Count Reconciliation (run ~7:45 PM ET)

Business date = today (America/New_York). Compare Bravo sold-jewelry vs the managers' handwritten AM/PM case counts, post to #jewlery-counts (C0BM9NHGTT4). Proven end-to-end 2026-07-31 — follow exactly; do not improvise.

## 1. Context first
Read the READ-FIRST INDEX (top ~60 lines) of `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/BRAVO_KNOWN_ISSUES.md`. Respect SOLVED / TRIED-AND-FAILED. Method reference: `/Users/joshuadavis/Documents/Claude/Projects/Jewelry Count Reconciliation/jewelry_reconciliation_comparison.py` and STATUS.md.

## 2. Bravo pull
- Confirm no unclaimed .json in `.../Bravo Data Extraction/triggers/` (top level only).
- Write `triggers/jewelry-count-recon-<YYYY-MM-DD>-auto.json` (unique id; append -b/-c if reused):
  {"id":"<id>","requested_at":"<now ISO -0400>","reports":[{"name":"jewelry-count-audit","stores":["CUL","HAR","LEX","ROA","WAY"],"date":"<date>"}]}
- Poll `results/<id>.result.json` every 30s, up to 20 min (strip UTF-8 BOM). 5 cells, ~2 min each.
- CSVs land at `output/<date>_to_<date>_<STORE>_jewelry-count-audit.csv`. They contain ALL sold items (tools, guns, games) — not just jewelry. Never treat row count as jewelry count.

## 3. Count sheets (vision pass)
Managers post sheet photos to #end-of-day (C03C7HV8L48) ~6:00-7:15 PM ET. Using Chrome (claude-in-chrome; if screenshots return 0x0 viewport, activate/resize Chrome via osascript first), open https://app.slack.com/client/T03BL4W1DCL/C03C7HV8L48 and for each store open the jewelry count photo (AM COUNT / PM COUNT columns: Rings, Bracelets, Necklaces, Earrings, Pendants). Zoom the block dated with the business date; read AM and PM per category.
- SUM-VERIFY every column against its written total; re-zoom if it does not add up.
- Identify store from the EOD summary sheet header ("END OF DAY: <STORE>"), NOT the poster.
  Poster map (verify vs headers): Bree/Bree Grayson=CUL, Walker Tapley=HAR, Uriah=LEX, Benjie Moore=ROA, Martin D./Martin Dowden=WAY, Sandi Cole=CUL (historic), Chadd=WAY (historic).
- Sheet date != business date -> FLAG, never silently correct.
- Store not posted yet -> wait 30 min once, then proceed marking it "no sheet posted".

## 4. Compute (per store)
Bucket each CSV row via jewelry_reconciliation_comparison.py rules: Category must be in the canonical JEWELRY_CATEGORIES set; then exclude scrap/bullion/wristwatch/pocket watch/watch band/brooch/misc and bare "Diamond"; then bracelet/bangle->Bracelets, earring->Earrings (BEFORE ring), ring/wedding band/solitaire->Rings, necklace/chain->Necklaces, pendant/charm->Pendants.
sold = bucket sum. net = AM_total - PM_total. diff = net - sold. FLAG if |diff| > 5 or date mismatch.

## 5. Post to #jewlery-counts (C0BM9NHGTT4)
The ONLY Slack output. Header "Jewelry Count Reconciliation — <date>"; per store one line:
:white_check_mark:/:triangular_flag_on_post: STORE — Bravo sold | AM -> PM | net | diff, plus a one-line plain-English note per flag (case grew = likely buys backfilling; unexplained shrink = manager check). Footer: sheets dated correctly + sum-verified status.

## 6. Record
Append run record (date, table, flags) to `.../Jewelry Count Reconciliation/STATUS.md`.

## Failure rules
Bravo pull fails -> retry ONCE with fresh id; never force-kill anything; never edit lib/ or reports/ files (Rule #4, additive only). Post the failure honestly to C0BM9NHGTT4 and record it in STATUS.md. A cloud watchdog checks the channel at 9:30 PM ET and alerts if nothing posted.