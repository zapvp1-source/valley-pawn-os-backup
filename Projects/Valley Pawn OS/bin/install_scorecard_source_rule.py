#!/usr/bin/env python3
"""install_scorecard_source_rule.py — stop the CEO briefs reporting working reports as dark.

WHY (2026-09-22): the Monday weekly scorecard told Joshua "daily intake-margin and sold-item-margin
reports went dark for the week." They posted 9/17, 9/18, 9/19, 9/21 and 9/22. The brief reads Slack
through the Cowork connector, which cannot see message text posted by the vp_ops_engine bot (a
different app) — the exact cross-app blindness that produced the three-day "pawn-walk posts empty
messages" phantom. A brief that reports healthy things as broken is worse than no brief.
"""
import datetime as dt, os, sys
SCHED = os.path.expanduser("~/Documents/Claude/Scheduled")
MARK = "SOURCE-OF-RECORD RULE for 'what published' (2026-09-22)"
BLOCK = """

---

# %s

**Never judge whether a report published by reading its channel through the Slack connector.**
Most Tier-1 reports are now posted by the `vp_ops_engine` bot — a different Slack app — and the
connector shows those messages as present-but-empty or misses them entirely. On 2026-09-21 this
brief reported the pawn walk and sold review "dark for the week"; they had posted every day. Joshua
read that as fact.

For every "did X publish / what did X say" question, read these instead, in this order:
1. `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/receipts/<task>.jsonl` — one
   line per real publication, with timestamp and the first line of what was sent.
2. `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/audit.json` — per task:
   hit/miss per instance, rate, last_good. Regenerated nightly.
3. `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/WHATS_ACTUALLY_BROKEN_2026-09-20.md`
   — the current day-by-day picture, maintained by the fleet owner.
4. The report's own output files (e.g. `Pawn Walks/daily/<date>_intake_margin_summary.json`) for
   the numbers themselves.

A channel read is acceptable ONLY for messages posted by people or by the Cowork app itself.
If none of the sources above has a task, say "not measured" — never "dark" or "didn't post."
"""
for task in ("ceo-weekly-scorecard", "ceo-monthly-scorecard"):
    p = os.path.join(SCHED, task, "SKILL.md")
    if not os.path.isfile(p):
        print("MISSING", task); continue
    body = open(p, encoding="utf-8").read()
    if MARK in body:
        print("already", task); continue
    if "--apply" not in sys.argv:
        print("WOULD ADD", task); continue
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    open(p + ".bak-source-" + stamp, "w", encoding="utf-8").write(body)
    open(p, "a", encoding="utf-8").write(BLOCK % MARK)
    print("ADDED", task)
