# V3 CELL (2026-10-06) — use jewelry-case-counts-v3, not v2

This REPLACES the cell name in STEP 2 / the HOST ACCESS pull line. Everywhere this file says `jewelry-case-counts-v2`, use **`jewelry-case-counts-v3`**:

    bash "$BIN/bravo_pull.sh" jewelry-case-counts-v3 <YYYY-MM-DD> <STORE> jewelry-onhand-<YYYY-MM-DD>-<STORE>

Same CSV path (`output/<date>_<STORE>_jewelry-case-counts.csv`), same columns, same result JSON shape. v2 stays registered as a fallback; use it only if a v3 trigger fails with "No handler" / "unknown report".

What v3 changes (proven live 2026-10-06 on Culpeper and Roanoke):
1. **Duplicate counts are now PROVEN, not refused.** When two categories share a number (Culpeper Charms 19 and Brooches 19 since 9/30, which is real inventory), v3 re-reads each one straight after a different-count category. A stale screen would show the other category's number, so a matching re-read proves the duplicate is real. Result `success` = trust all 8 rows. **Do NOT override a v3 "Duplicate counts..." error by hand any more** (the 9/30 and 10/1 runs did that with v2). With v3 that error means the re-check actually disagreed, so it is a real Bravo-side failure: follow the failure path.
2. **Faster, lower-risk report picking.** v3 picks each saved report in one click plus typing (about 5 seconds) and only falls back to v2's long open/close sequence if that does not verify. That long sequence is where the nightly wedges froze (log stops dead, 40-minute wrapper timeout).

Unchanged: the EMPTY-CATEGORY RULE in STEP 4. A Charms or Brooches row with status=error is still treated as 0 ONLY when the same store+category was also error/0 in the most recent prior-day CSV (as of 10/6 that applies to HAR Charms, LEX Charms, LEX Brooches and WAY Charms). v3 still never writes a 0 itself.
