import re

GATE = """
## STEP 0 — OPEN-STORES GATE (Joshua, 2026-08-12). Do this before anything else.

Only pull stores that ACTUALLY TRADED TODAY. A store that was closed all day has no new
count sheet, so pulling it produces a number with nothing to compare it against. Do not
pull closed stores "for an integrity check" — Joshua's instruction is to skip them.

Store hours:
- Culpeper (CUL): open Mon-Sat.
- Harrisonburg (HAR), Waynesboro (WAY), Lexington (LEX), Roanoke (ROA):
  open Mon, Tue, Thu, Fri, Sat. CLOSED WEDNESDAY.
- All 5 closed Sunday.

So the store list for tonight is:
- Sunday                      -> NOBODY IS OPEN. Skip the entire run. Pull nothing, post
                                 nothing, DM nothing. This is a correct no-op, not a failure.
- Wednesday                   -> ["CUL"] only.
- Mon, Tue, Thu, Fri, Sat     -> ["CUL","HAR","LEX","ROA","WAY"]

Get the real weekday first — do not assume:
    date '+%A %Y-%m-%d'
via mcp__Control_your_Mac__osascript. Use that result to build the store list, and use that
same list everywhere below (the trigger JSON, the completeness check, and your run output).
"COMPLETE" means every OPEN store returned a count. It does not mean five stores.
"""

# ---------- PULL TASK ----------
p = '/Users/joshuadavis/Documents/Claude/Scheduled/jewelry-onhand-nightly-pull/SKILL.md'
s = open(p).read()

# 1. Replace the old "pull all 5 anyway" nuance block.
old_start = 'STORE-CLOSURE NUANCE'
i = s.find(old_start)
if i != -1:
    j = s.find('STEP 1', i)
    s = s[:i] + 'STORE HOURS: see STEP 0 above — pull OPEN stores only.\n\n' + s[j:]

# 2. Hard-code list -> open-store list in the trigger schema.
s = s.replace('"stores": ["CUL","HAR","LEX","ROA","WAY"]',
              '"stores": <OPEN STORES FOR TODAY from STEP 0 — e.g. ["CUL"] on a Wednesday>')

# 3. Completeness wording.
s = s.replace('confirm all 5 CSVs exist for today',
              'confirm a CSV exists for every OPEN store from STEP 0 (not necessarily 5)')
s = s.replace('Expect roughly 45-60 minutes for 5 stores.',
              'Expect roughly 10-12 minutes per store (so ~10 min on a Wednesday, ~50 min on a full day).')

# 4. Insert the gate right after the frontmatter/title area.
anchor = '═══ RULE 0'
k = s.find(anchor)
s = s[:k] + GATE.strip() + '\n\n' + s[k:] if k != -1 else GATE.strip() + '\n\n' + s
open(p, 'w').write(s)
print('patched PULL:', p)

# ---------- COMPARE TASK ----------
p2 = '/Users/joshuadavis/Scheduled/placeholder'
p2 = '/Users/joshuadavis/Documents/Claude/Scheduled/jewelry-onhand-nightly-compare/SKILL.md'
s2 = open(p2).read()

i2 = s2.find('STORE-CLOSURE NUANCE')
if i2 != -1:
    j2 = s2.find('STEP 1', i2)
    s2 = s2[:i2] + ('STORE HOURS — compare OPEN stores only (Joshua, 2026-08-12).\n'
                    'Closed stores are not pulled any more, so there is nothing to compare for them.\n'
                    'Wednesday = CUL only. Sunday = no run at all. Mon/Tue/Thu/Fri/Sat = all 5.\n'
                    'Get the weekday from `date \'+%A\'` first. "Complete" means every OPEN store\n'
                    'compared — a Wednesday run with only Culpeper is COMPLETE, not partial.\n\n') + s2[j2:]

s2 = s2.replace('the count of exact cells out of the 25 (5 stores x 5 categories)',
                'the count of exact cells out of the total for the day (open stores x 5 categories)')
open(p2, 'w').write(s2)
print('patched COMPARE:', p2)
