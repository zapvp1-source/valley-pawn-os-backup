p = '/Users/joshuadavis/Documents/Claude/Scheduled/jewelry-onhand-nightly-compare/SKILL.md'
s = open(p).read()

anchor = "STEP 4 — Analyze, don't just tabulate."
addition = """STEP 3b — REPORT POLARITY: always OVER / SHORT from the SHEET's point of view (Joshua, 2026-08-12).

Bravo is the EXPECTED count. The manager's PM sheet is the ACTUAL physical count. Every variance is
stated as what the SHEET is doing relative to expected:

    variance = SHEET count - BRAVO count
    positive -> "OVER n"    (more pieces physically counted than the system expects)
    negative -> "SHORT n"   (fewer pieces physically counted than the system expects)
    zero     -> "MATCH"

Never report the raw Bravo-minus-sheet number and never use bare +/- signs. Use the words OVER, SHORT,
MATCH. Give a per-category line and a store total, plus the count of MATCH cells out of 25.

DIRECTION MATTERS — they mean different things:
- SHORT is the structurally expected direction right now, because Bravo counts all on-hand jewelry
  (case + safe + back stock + bins) while the manager counts the DISPLAY CASE ONLY. A SHORT variance is
  most likely stock sitting outside the case. Do NOT call it loss.
- OVER is the anomalous direction and gets the sharpest attention: more pieces physically in the case
  than exist in the system for that category. That means stock not entered, or stock categorized in
  Bravo under a category this report does not select (confirmed real: ROA had pendants entered as
  charms, 2026-08-12).

"""

assert anchor in s
s = s.replace(anchor, addition + anchor)
open(p, 'w').write(s)
print('OK - polarity convention added')
