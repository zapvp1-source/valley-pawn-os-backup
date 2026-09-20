#!/usr/bin/env python3
"""fleet_replay.py — replay REAL recorded history through the alarm that exists now.

WHY (2026-09-19): the sandbox proves the detectors work on synthetic faults. It cannot answer the
question Joshua actually cares about: *would this have caught 9/14?* Waiting for the next outage to
find out is the same trap as waiting a week — except worse, because the answer arrives only when it
is too late to matter.

We do not have to wait. Sixty days of real outcomes are already measured in fleet/audit.json: which
publication missed, on which date, since its own inception. This walks that history forward day by
day and applies the CURRENT fleet-event rule to it, producing the alert timeline Joshua would have
received had this code existed in July.

THE RULE IS IMPORTED, NOT RETYPED. `FLEET_EVENT_MIN` comes from field_scorecard.py itself. A replay
that hardcodes its own threshold is testing a rule nobody ships — it would go green while production
used a different number, which is a worse outcome than no replay at all.

Honest limits, since this is evidence and will be quoted:
  * It replays MISSES, which is what the audit records. It cannot replay a run that produced a wrong
    number — accuracy is a separate axis (see the `_corrected` notes in the manifest).
  * Per-task miss history is capped at the audit's retention, so a very old event may be partial.
  * It proves the ALARM would have fired. Whether anyone acted on the DM is not a code question.

    fleet_replay.py [--json fleet/audit.json]
"""
import collections
import datetime as dt
import json
import os
import sys

OS_DIR = os.path.expanduser("~/Documents/Claude/Projects/Valley Pawn OS")
sys.path.insert(0, os.path.join(OS_DIR, "bin"))
try:
    import field_scorecard as fs
    THRESHOLD = fs.FLEET_EVENT_MIN
    SOURCE = "imported from field_scorecard.py"
except Exception as e:                       # never silently substitute a guess for the real rule
    THRESHOLD = None
    SOURCE = "UNAVAILABLE (%s)" % e


def main():
    if THRESHOLD is None:
        print("REFUSED: could not import the live fleet-event threshold (%s)." % SOURCE)
        print("Replaying against a guessed threshold would test a rule that is not in production.")
        return 2
    p = sys.argv[sys.argv.index("--json") + 1] if "--json" in sys.argv else os.path.join(OS_DIR, "fleet/audit.json")
    rows = json.load(open(p))
    measured = [r for r in rows if r.get("status") == "MEASURED"]

    by_date = collections.defaultdict(list)
    for r in measured:
        for d in (r.get("dark_dates") or []):
            by_date[d].append(r["task"])
    if not by_date:
        print("no recorded misses in %s — nothing to replay" % p)
        return 0

    # dark_dates are MM/DD; infer the year from the audit window (it spans a single year here)
    year = dt.datetime.now().year
    def key(md):
        m, d = md.split("/")
        return dt.date(year, int(m), int(d))
    dates = sorted(by_date, key=key)

    print("# Replay — what the fleet-event alarm WOULD have done, against real recorded history\n")
    print("Threshold: %d+ unrelated publications missing on one day (%s).\n" % (THRESHOLD, SOURCE))
    print("| Date | Missed | Alarm | What Joshua would have been told |")
    print("|---|---:|---|---|")

    prev = None
    day_n = 0
    events = []
    alerts = 0
    silent_days = 0
    for md in dates:
        n = len(by_date[md])
        cur = key(md)
        if n >= THRESHOLD:
            day_n = day_n + 1 if (prev and (cur - prev).days == 1) else 1
            if day_n == 1:
                events.append({"start": md, "days": 1, "peak": n})
            else:
                events[-1]["days"] = day_n
                events[-1]["peak"] = max(events[-1]["peak"], n)
            alerts += 1
            msg = ("one shared thing is down, not %d separate problems" % n) if day_n == 1 \
                  else ("Day %d — this has been going on since %s" % (day_n, events[-1]["start"]))
            print("| %s | %d | **ALERT day %d** | %s |" % (md, n, day_n, msg))
            prev = cur
        else:
            silent_days += 1
            day_n = 0
            prev = None
            print("| %s | %d | quiet | below threshold — individual miss handling |" % (md, n))

    print("\n## Distinct outages the alarm would have caught\n")
    print("| Started | Ran | Peak tasks down | Caught on |")
    print("|---|---:|---:|---|")
    for e in events:
        print("| %s | %d day(s) | %d | **day 1 (%s)** |" % (e["start"], e["days"], e["peak"], e["start"]))

    worst = max(events, key=lambda e: e["days"]) if events else None
    print("\n## What this is worth\n")
    print("- **%d distinct outages** would have been flagged, every one of them on **day 1**." % len(events))
    print("- **%d alert-days** in total; %d days stayed quiet (correctly — below threshold)." % (alerts, silent_days))
    if worst:
        print("- The worst ran **%d days** from %s, peaking at **%d publications down at once**."
              % (worst["days"], worst["start"], worst["peak"]))
        print("  In reality nobody was told, because the watchdog had been dead for an unknown")
        print("  length of time (the state-shadowing bug fixed 2026-09-18). Under the current code")
        print("  that outage is a DM on its first morning, and an escalating one every day after.")
    print("\nThis replays MISSES, which is what the audit records. A run that produced a WRONG")
    print("number is a separate axis and is not claimed here.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
