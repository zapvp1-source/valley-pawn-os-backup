#!/bin/bash
set +e
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
bash "$BIN/append_line.sh" "$HOME/Documents/Claude/Projects/Jewelry Count Reconciliation/STATUS.md" '
## Run record — 2026-09-18 (Friday, all 5 stores open)

Freeze window: 6:00 PM close -> 10:00 AM reopen, all 5 stores. Bravo touched 8:37 PM-10:23 PM ET via the host job queue (bravo_pull.sh, one job per store, processed one at a time by the shared watcher), inside the window for every store.

Per-store outcome (jewelry-case-counts-v2, 8 Bravo categories each):
- CUL: success first pull, all 8 categories status=ok. Rings 670, Bracelets 118, Pendants 224, Charms 20, Brooches 18, Earrings 144, Chains 83, Necklaces 66.
- HAR: 7/8 ok first pull (Charms failed); Charms also error on 2026-09-17 (most recent prior day), so treated as 0 per the confirmed-empty-category rule. Rings 460, Bracelets 47, Pendants 115, Charms 0(rule), Brooches 2, Earrings 46, Chains 66, Necklaces 46.
- LEX: 7/8 ok first pull (Brooches failed); Brooches also error on 2026-09-17, treated as 0 per rule. Rings 290, Bracelets 39, Pendants 55, Charms 1, Brooches 0(rule), Earrings 47, Chains 29, Necklaces 18.
- ROA: success first pull, all 8 categories status=ok. Rings 568, Bracelets 140, Pendants 112, Charms 65, Brooches 2, Earrings 79, Chains 98, Necklaces 68.
- WAY: first pull wedged mid-run (combo-select stall on Pendants, no log progress for about 16 minutes; the run self-healed once via watcher restart but never produced a result and the pull process eventually exited with no result file). Retried once per policy (jewelry-onhand-2026-09-18-WAY-retry): 7/8 ok (Charms failed); Charms also error on 2026-09-17, treated as 0 per rule. Rings 335, Bracelets 45, Pendants 59, Charms 0(rule), Brooches 5, Earrings 59, Chains 47, Necklaces 25.

Repeat-pattern watch: HAR Charms, LEX Brooches, and WAY Charms all read error (empty) again tonight, each matching the same store+category being error on 2026-09-17 too — stable known gaps, not new anomalies. WAY mid-run stall is a new wrinkle worth watching if it recurs; the retry completed cleanly on the second attempt.

Completeness: all 5 open stores complete (CUL, HAR, LEX, ROA, WAY), all 40 category reads accounted for (37 status=ok + 3 confirmed-empty treated as 0).

Freeze-window confirmation:
- Bravo side (live on-hand pulls): 2026-09-18 20:37 PM-22:23 PM ET, inside the 6PM close to next-day 10AM freeze window for all 5 stores.
- Sheet side (PM count, #end-of-day): Walker Tapley (HAR) 6:10 PM, Uriah (LEX) 6:16 PM, Benjie Moore (ROA) 6:16 PM, Chadd (WAY) 6:28 PM, Sandi (CUL) 6:30 PM, all posted after 6PM close, inside freeze window.

Per-store table (Expected = Bravo on-hand, Counted = PM sheet, Variance = Counted-Expected):
CUL: Rings 670/670 (0), Bracelets 118/117 (-1), Earrings 144/144 (0), Pendants 262/262 (0), Necklaces 149/149 (0), Total 1343/1342 (-1)
HAR: Rings 460/460 (0), Bracelets 47/47 (0), Earrings 46/47 (+1), Pendants 117/117 (0, Charms treated as 0), Necklaces 112/115 (+3), Total 782/786 (+4)
LEX: Rings 290/293 (+3), Bracelets 39/40 (+1), Earrings 47/47 (0), Pendants 56/55 (-1, Brooches treated as 0), Necklaces 47/47 (0), Total 479/482 (+3)
ROA: Rings 568/568 (0), Bracelets 140/140 (0), Earrings 79/79 (0), Pendants 179/177 (-2), Necklaces 166/168 (+2), Total 1132/1132 (0)
WAY: Rings 335/335 (0), Bracelets 45/45 (0), Earrings 59/59 (0), Pendants 64/64 (0, Charms treated as 0), Necklaces 72/72 (0), Total 575/575 (0)

Repeat check: no store/category variance repeats night-over-night at meaningful scale. HAR and LEX overs of +3/+4 are small, ordinary count-timing noise, nowhere near the ROA-pendants-as-charms scale of concern (about +61). No anomalous OVER variance. No DM sent to Joshua per STEP 7 — clean night aside from the WAY mid-run stall, noted above and resolved by retry.

Posted to #jewlery-counts: https://valleypawnworkspace.slack.com/archives/C0BM9NHGTT4/p1789784795047409
'
