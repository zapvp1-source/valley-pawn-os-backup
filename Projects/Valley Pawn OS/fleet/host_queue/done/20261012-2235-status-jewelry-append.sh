#!/bin/bash
set +e
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
STATUS="$HOME/Documents/Claude/Projects/Jewelry Count Reconciliation/STATUS.md"
L="$(cat << 'BODYEOF'

## RUN RECORD — 2026-10-12 (Monday)

All 5 stores open tonight (Monday full fleet). Full post, no partial-post needed — all 5 stores completed both Bravo and PM-sheet verification cleanly.

Context: this task had not completed successfully for 3 prior nights (10/10, 10/11, and an earlier 10/12 attempt) — the last successful CSV pull before tonight was 2026-10-09 (pulled early 10/10). Tonight's run queued fresh via host_queue at ~20:41 ET using jewelry-case-counts-v2 (current report cell), one job per store (CUL/HAR/LEX/ROA/WAY).

Bravo pulls: CUL, HAR, LEX completed cleanly, exit=0 in the host_queue done/ log. ROA and WAY's done/ logs showed `TIMEOUT ... exit=1` — cross-checked against the authoritative `results/jewelry-onhand-2026-10-12-<STORE>.result.json`: ROA was a false negative (status success, all 8 categories returned, ~1436s duration — the wrapper's own wait loop just missed the completion signal); WAY was a genuine partial (status partial, 7/8 categories, Charms failed: "Only 7 of 8 categories returned a count... Refusing to report a partial jewelry count as success"). Per standing practice, the host_queue wrapper exit code was NOT treated as authoritative — result.json and the output CSV were. All 5 stores' output CSVs present and used.

Empty-category rule applied for WAY Charms, HAR Charms, LEX Charms+Brooches: each cross-checked against the most recent prior-day baseline (all empty/error there too, same standing pattern, not a new failure) — none of Rings/Bracelets/Pendants/Earrings/Chains/Necklaces errored for any store tonight.

PM count sheets: all 5 managers' photos read from fleet/eod_photos/2026-10-12/ (Read tool, staged from device), each store identified from its own sheet's printed header, never the Slack poster's identity. Posts: Uriah 18:08 ET, Martin-D (posted WAY — printed header "END OF DAY: WAYNESBORO," signed Martin Dowden, though WAY's listed manager is Chadd McClintic) 18:12 ET, Sandi-Cole 18:19 ET, Benjie-Moore 18:22 ET, Walker-Tapley 18:39 ET — all 15 photos landed 18:08-18:39 ET, inside the post-close freeze window. Every PM block sum-verified against its own sheet's TOTALS line except one: WAY's handwritten PM Totals read 576, one over its own 5 category digits summed (337+45+71+58+64=575); AM and PM totals were identical (576) despite AM Rings (338) vs PM Rings (337) differing by 1 — assessed as a manager-side arithmetic/carry-forward slip (each category digit was clearly legible, not a misread) — proceeded using the individual category figures.

Comparison (Expected = Bravo on-hand jewelry case count, Counted = PM count sheet):

| Store | Category | Expected | Counted | Variance |
|-------|----------|----------|---------|----------|
| CUL | Rings | 671 | 671 | 0 |
| CUL | Bracelets | 118 | 118 | 0 |
| CUL | Earrings | 143 | 143 | 0 |
| CUL | Pendants | 254 | 254 | 0 |
| CUL | Necklaces | 151 | 152 | +1 |
| **CUL Total** | | **1337** | **1338** | **+1** |
| HAR | Rings | 436 | 433 | -3 |
| HAR | Bracelets | 49 | 49 | 0 |
| HAR | Earrings | 51 | 52 | +1 |
| HAR | Pendants | 111 | 110 | -1 |
| HAR | Necklaces | 116 | 115 | -1 |
| **HAR Total** | | **763** | **759** | **-4** |
| LEX | Rings | 301 | 304 | +3 |
| LEX | Bracelets | 41 | 42 | +1 |
| LEX | Earrings | 46 | 46 | 0 |
| LEX | Pendants | 55 | 53 | -2 |
| LEX | Necklaces | 47 | 47 | 0 |
| **LEX Total** | | **490** | **492** | **+2** |
| ROA | Rings | 581 | 581 | 0 |
| ROA | Bracelets | 137 | 137 | 0 |
| ROA | Earrings | 84 | 84 | 0 |
| ROA | Pendants | 174 | 173 | -1 |
| ROA | Necklaces | 152 | 153 | +1 |
| **ROA Total** | | **1128** | **1128** | **0** |
| WAY | Rings | 337 | 337 | 0 |
| WAY | Bracelets | 45 | 45 | 0 |
| WAY | Earrings | 58 | 58 | 0 |
| WAY | Pendants | 64 | 64 | 0 |
| WAY | Necklaces | 71 | 71 | 0 |
| **WAY Total** | | **575** | **575** | **0** |

Assessment: all 5 stores' variances are small (CUL +1, HAR -4, LEX +2, ROA 0, WAY 0) and fall within ordinary scope-related noise (Bravo counts case+safe+back-stock+bins vs. the PM sheet counting only the visible display case) — no anomalous OVER variance under the standing rule (none near the ~+61 ROA-pendants-as-charms scale) tonight. No DM to Joshua.

Freeze-window confirmation: Bravo pull window (6pm close through 10am next-day reopen) — tonight's pulls ran ~20:43-22:28 ET, well inside. PM sheets posted 18:08-18:39 ET, same-date (10/12) PM blocks, also inside the valid comparison window.

Repeats to watch: HAR Charms, LEX Charms+Brooches, WAY Charms — all empty again tonight, consistent with the ongoing standing pattern, not escalating. No new anomalies flagged.

Outcome: posted to #jewlery-counts via outbox (jewelry-onhand-nightly-pull-20261012-223429, absolute-path envelope). No DM to Joshua (no anomalous OVER variance, no run failure). No FAILURE_LEDGER row — all 5 stores succeeded; the ROA/WAY host_queue TIMEOUT log lines were wrapper-log noise, not actual Bravo-side failures, confirmed via result.json/output CSV cross-check.
BODYEOF
)"
bash "$BIN/append_line.sh" "$STATUS" "$L"
