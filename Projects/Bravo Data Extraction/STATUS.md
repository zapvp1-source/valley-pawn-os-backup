# Jewelry On-Hand Nightly Pull — Run Records

## 2026-08-17 (Monday) — jewelry-onhand-nightly-pull

**Run window:** ~6:12 PM – 11:09 PM ET (extended by CUL combo-select flakiness; no manual intervention per task rules — retry logic ran on its own)

**Bravo pull (system on-hand, 8 categories x 5 stores):**
- CUL: success, 8/8 categories
- HAR: partial — Charms returned no rows (empty-category error, not a false zero). Cross-checked against 2026-08-15 CSV, Charms was also empty that day. Treated as 0 in tonight's table per the empty-category rule.
- LEX: partial — Brooches returned no rows (empty-category error). Cross-checked against 2026-08-15 CSV, Brooches was also empty. Treated as 0 in tonight's table per the empty-category rule.
- ROA: success, 8/8 categories
- WAY: success, 8/8 categories

**PM count sheets (#end-of-day):**
- CUL (Sandi, 6:12 PM): read and sum-verified against written total (1461). Match.
- HAR (Walker Tapley, 6:19 PM): read and sum-verified against written total (796). Match.
- ROA (Benjie Moore, 6:35 PM): read and sum-verified against written total (1089). Match.
- WAY (Chadd, 6:24 PM): individual category digits re-zoomed and confirmed unambiguous (378/42/66/51/66), but they do NOT sum to the sheet's own written total (563 written vs 603 actual sum). Treated as a manager arithmetic error, not a misread — used the individual digits, not the written total.
- LEX: **no PM count sheet posted to #end-of-day at any point tonight** (channel searched in full through 11:09 PM). Excluded from tonight's variance table — no data guessed or assumed. Bravo's expected-side numbers for LEX were pulled successfully and are on disk (2026-08-17_LEX_jewelry-case-counts.csv) for whenever/if a sheet shows up.

**Variance table:** posted to #jewlery-counts at 2026-08-17 ~11:10 PM ET. https://valleypawnworkspace.slack.com/archives/C0BM9NHGTT4/p1787022631315899

Store totals (Expected/Counted/Variance):
- CUL: 1462 / 1461 / -1
- HAR: 797 / 796 / -1
- ROA: 1088 / 1089 / +1
- WAY: 565 / 603 / +38 (driven almost entirely by Rings: 339 expected vs 378 counted)
- LEX: not compared — sheet missing

**Anomalies flagged / DM sent to Joshua (D03BHQH5VGT):**
1. WAY Rings +39 over expected (339 vs 378) — WAY's own count sheet doesn't even sum to its written total, points to a manager count/math issue at WAY rather than a Bravo pull error. Needs a look.
2. LEX PM sheet never posted tonight — flagged so it doesn't silently fall through the cracks.
3. HAR Charms / LEX Brooches empty-category-treated-as-zero noted per standing rule.

**Guardrails followed:** no manual Bravo UI interaction (let CUL's retry/fallback logic run on its own even though one category took ~35-50 min), no folder-access request needed (bash/file tools sufficed), no false zeros reported (empty categories cross-checked against prior day before being treated as 0), no partial/guessed post for LEX.
