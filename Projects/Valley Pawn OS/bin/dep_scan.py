#!/usr/bin/env python3
"""dep_scan.py — which scheduled tasks still depend on the osascript/Control_your_Mac path?

WHY (2026-09-20): the 9/12-9/17 outage was caused by that connector vanishing from scheduled
sessions. It was fixed on 9/17 by converting ELEVEN DAILY tasks to native launchd agents. The
WEEKLY Monday chain was never converted — and the registry shows all 12 weeklies FIRED on 9/14 and
published nothing. If they still require that connector, Monday 9/21 fails exactly the same way.
This lists who is still exposed, so the answer is a fact and not a guess.
"""
import os, re, sys
SCHED = os.path.expanduser("~/Documents/Claude/Scheduled")
PAT = re.compile(r"Control_your_Mac|osascript", re.I)
NATIVE = re.compile(r"launchd|com\.valleypawn\.|host_queue|vp-runner", re.I)
WEEKLY = ["monday-bravo-combined-run","monday-bravo-combined-compile","monday-bravo-postcheck",
          "monday-bravo-cell-gapfill","weekly-store-kpis","weekly-returns-summary",
          "nics-weekly-mtd-ranking","layaway-yield-weekly","review-obtained-last-week",
          "weekly-markdown-verification-pull","weekly-markdown-verification-review",
          "weekly-timekeeping-analysis"]
print("# osascript exposure — the Monday chain\n")
print("| Task | mentions osascript | mentions a native/host-queue path | verdict |")
print("|---|---:|---:|---|")
exposed=[]
for t in WEEKLY:
    p = os.path.join(SCHED, t, "SKILL.md")
    if not os.path.isfile(p):
        print("| %s | - | - | NO SKILL.md |" % t); continue
    s = open(p, errors="replace").read()
    n_os, n_nat = len(PAT.findall(s)), len(NATIVE.findall(s))
    if n_os and not n_nat:
        v = "**EXPOSED** — will fail again if the connector is absent"; exposed.append(t)
    elif n_os and n_nat:
        v = "mixed — has a fallback, verify it"
    elif n_nat:
        v = "native/host-queue path"
    else:
        v = "no host-shell dependency (browser/API task)"
    print("| %s | %d | %d | %s |" % (t, n_os, n_nat, v))
print("\nSUMMARY exposed=%d" % len(exposed))
for t in exposed: print("- %s" % t)
