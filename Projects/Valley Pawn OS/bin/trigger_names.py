#!/usr/bin/env python3
"""trigger_names.py — extract the Bravo report/trigger names each Monday task needs.

WHY (2026-09-20): converting the Monday chain to native requires knowing exactly which reports it
pulls. Guessing the trigger names would produce a pull that silently returns nothing — the same
silent-success failure this whole effort exists to eliminate. So read them out of the SKILLs.
"""
import os, re, json
SCHED = os.path.expanduser("~/Documents/Claude/Scheduled")
BD = os.path.expanduser("~/Documents/Claude/Projects/Bravo Data Extraction")
TASKS = ["monday-bravo-combined-run","monday-bravo-combined-compile","monday-bravo-postcheck",
         "monday-bravo-cell-gapfill","weekly-store-kpis","layaway-yield-weekly",
         "weekly-markdown-verification-pull","nics-weekly-mtd-ranking","weekly-returns-summary"]
NAME = re.compile(r'"name"\s*:\s*"([a-z0-9\-]+)"')
REP  = re.compile(r'\b(aged-inventory|store-rankings|employee-sales|loan-detail|layaway-detail|'
                  r'chekkit-inactives|intake-detail|sold-discount-detail|items-to-price|'
                  r'safe-register-journal|jewelry-case-counts|markdown[a-z\-]*|returns[a-z\-]*)\b', re.I)
print("# Bravo reports the Monday chain pulls\n")
allr = {}
for t in TASKS:
    p = os.path.join(SCHED, t, "SKILL.md")
    if not os.path.isfile(p):
        print("- **%s** — no SKILL.md" % t); continue
    s = open(p, errors="replace").read()
    names = sorted(set(NAME.findall(s)))
    reps = sorted({r.lower() for r in REP.findall(s)})
    for r in reps: allr.setdefault(r, []).append(t)
    print("- **%s**" % t)
    print("  - trigger `\"name\"` values found: %s" % (", ".join(names) or "none"))
    print("  - report keywords: %s" % (", ".join(reps) or "none"))
print("\n## Distinct reports the Monday pull must fetch\n")
for r, ts in sorted(allr.items()):
    print("- **%s** — needed by %s" % (r, ", ".join(ts)))
print("\n## Existing handlers on disk (proof these report names are real)\n")
h = os.path.join(BD, "handlers")
if os.path.isdir(h):
    for f in sorted(os.listdir(h))[:40]: print("- %s" % f)
else:
    print("(no handlers dir at %s)" % h)
