import os

p = '/Users/joshuadavis/Documents/Claude/Projects/Life OS/OPEN_ITEMS_REGISTER.md'

entry = (
    "\n| 2026-08-12 | Valley Pawn | Jewelry count reconciliation is NOT reconciling - only 5 of 25 "
    "category cells matched exactly on the first valid freeze-window comparison (8/11 PM manager "
    "sheets vs the 8/12 pre-open Bravo pull). Root cause: the 'Claude Jewelry Audit' saved reports "
    "export no Location column, so they count ALL on-hand jewelry (case + safe + back-stock + bins) "
    "while managers count the DISPLAY CASE ONLY. Nightly compare task threshold corrected to "
    "zero-tolerance (was wrongly accepting +/-1-3 as a match). BRAVO_KNOWN_ISSUES.md 2026-08-09 "
    "'no Location filter needed' entry REOPENED - it was closed on that bad tolerance plus a "
    "time-mismatched one-store comparison. | OPEN - needs the 'Claude Case Jewelry' saved report "
    "(jewelry categories + Location column) built in Bravo, then identify the location subset that "
    "equals the manager count. SEPARATE ISSUE: ROA Pendants reads 87 in Bravo vs 148 physically "
    "counted - Bravo is LOWER, which cannot be a location-scope effect and needs its own look. | "
    "Joshua |\n"
)

if os.path.exists(p):
    with open(p, 'a') as f:
        f.write(entry)
    print('appended to existing register')
else:
    with open(p, 'w') as f:
        f.write('# Open Items Register\n\n')
        f.write('| Date | Domain | What happened | Status / next step | Owner |\n')
        f.write('|---|---|---|---|---|\n')
        f.write(entry)
    print('created register and appended')
