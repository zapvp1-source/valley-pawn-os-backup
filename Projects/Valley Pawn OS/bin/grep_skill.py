#!/usr/bin/env python3
"""grep_skill.py — look inside a scheduled task's SKILL.md, or today's ledger rows.

WHY: an interactive session cannot read ~/Documents/Claude/Scheduled. When a task misses, the two
questions are always (a) did the edit we made actually land in its instructions, and (b) did the run
leave a reason behind. Answering those by guesswork is how three days got spent on a phantom defect.
"""
import os, sys
HOME = os.path.expanduser("~")
SCHED = os.path.join(HOME, "Documents/Claude/Scheduled")
LEDGER = os.path.join(HOME, "Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md")
if "--ledger" in sys.argv:
    day = sys.argv[sys.argv.index("--ledger") + 1]
    rows = [l for l in open(LEDGER, errors="replace") if day in l]
    print("%d ledger row(s) mentioning %s\n" % (len(rows), day))
    for r in rows[-6:]:
        print("- " + r.strip()[:700] + "\n")
    raise SystemExit(0)
task, needle = sys.argv[1], sys.argv[2]
p = os.path.join(SCHED, task, "SKILL.md")
if not os.path.isfile(p):
    print("no SKILL.md for %s" % task); raise SystemExit(1)
s = open(p, errors="replace").read()
print("SKILL.md: %d bytes" % len(s))
print("contains %r: %s" % (needle, needle in s))
i = s.find(needle)
if i >= 0:
    print("\n--- context ---")
    print(s[max(0, i-200):i+900])
