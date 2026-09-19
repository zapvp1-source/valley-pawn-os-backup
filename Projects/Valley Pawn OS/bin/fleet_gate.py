#!/usr/bin/env python3
"""fleet_gate.py — the keep / fix / kill verdict for every Tier-1 publication.

WHY: "decide if it's good to go or not based on accuracy and consistency" (Joshua, 2026-09-18).
A verdict Claude reasons out in a session is not reproducible — the same fleet would score
differently on a different day depending on what the session happened to look at. This applies the
FLEET_PLAN_V2 gate mechanically to the audit's own numbers, so the verdict is the same every time
and anyone can check the arithmetic.

THE GATE (all five must hold for GO):
  1. delivery rate  >= 95%
  2. longest dark run <= 1 consecutive missed instance
  3. accuracy incidents == 0      (a `_corrected*` note in the manifest = a wrong number went out)
  4. VERIFIABLE   — the audit can observe its output at all
  5. TESTABLE     — it can be exercised in isolation (native --render, or a Tier-1 SKILL carrying
                    the publish-guard precondition)

VERDICTS
  GO         — meets the gate. Leave it alone.
  REMEDIATE  — delivers something, but not reliably enough to trust unattended. Has a named defect
               class, so it has a fix.
  RETIRE     — never delivered inside its window since inception. It is not a broken report, it is
               an imaginary one: nobody has been receiving it, and nobody has complained. Retire it
               or rebuild it deliberately — do not keep paying for a run that produces nothing.
  NO EVIDENCE— receipts not yet written / surface unreadable. NOT a failure. Cannot be judged, and
               is never reported as broken (Rule 19: never prove a negative from a source that does
               not record it).

    fleet_gate.py --json fleet/audit.json        # score an audit dump
"""
import json
import os
import sys

OS_DIR = os.path.expanduser("~/Documents/Claude/Projects/Valley Pawn OS")
RATE_FLOOR = 95.0
DARK_CEILING = 1


def verdict(r):
    st = r.get("status")
    if st in ("AWAITING RECEIPTS", "NOT MEASURABLE", "MTIME ONLY", "NO ACCESS"):
        return "NO EVIDENCE", st.lower()
    if st != "MEASURED":
        return "NO EVIDENCE", (st or "unknown").lower()
    exp = r.get("expected") or 0
    if exp == 0:
        return "NO EVIDENCE", "no instance has come due since inception"
    rate = r.get("rate")
    rate = 0.0 if rate is None else rate
    dark = r.get("longest_dark") or 0
    acc = r.get("accuracy_notes") or 0
    if r.get("hit", 0) == 0:
        # A task that PRODUCED its artifact but outside the window is off-SCHEDULE, not absent.
        # Calling that RETIRE would recommend deleting something that actually runs — a delete
        # recommendation has to clear a higher bar than a fix recommendation.
        if r.get("late"):
            return "REMEDIATE", ("0 of %d on schedule since %s, but %d produced late — it runs, "
                                 "it does not run on its day" % (exp, r.get("since"), r["late"]))
        if exp < 3:
            return "NO EVIDENCE", ("0 of %d since %s — too few instances to justify retiring "
                                   "(needs 3). Watch it." % (exp, r.get("since")))
        return "RETIRE", "0 of %d delivered since %s — has never worked" % (exp, r.get("since"))
    why = []
    if rate < RATE_FLOOR:
        why.append("%.1f%% delivery (floor %.0f%%)" % (rate, RATE_FLOOR))
    if dark > DARK_CEILING:
        why.append("%d consecutive misses (ceiling %d)" % (dark, DARK_CEILING))
    if acc:
        why.append("%d accuracy incident(s)" % acc)
    if r.get("late"):
        why.append("%d backfilled, not run on the day" % r["late"])
    if not why:
        return "GO", "%.1f%%, longest dark %d, no accuracy incidents" % (rate, dark)
    return "REMEDIATE", "; ".join(why)


def shape(r):
    """The defect CLASS, which is what decides the fix. Two tasks at the same rate can need
    completely different work: a long dark run is infrastructure (something was down for days),
    scattered singles are flakiness (it fires and dies mid-run)."""
    dark = r.get("longest_dark") or 0
    miss = r.get("miss") or 0
    if miss == 0:
        return "-"
    if dark >= 4:
        return "OUTAGE — %d in a row; infrastructure, not the task" % dark
    if dark <= 2 and miss >= 3:
        return "FLAKY — %d scattered misses; fires then dies mid-run" % miss
    return "MIXED — %d misses, longest run %d" % (miss, dark)


FLEET_EVENT_MIN = 5


def fleet_events(rows):
    """Dates where many unrelated tasks missed at once.

    This is the difference between a diagnosis and a list. 25 tasks each at 60% looks like 25 broken
    tasks and 25 repairs; if their misses land on the SAME handful of dates, it is a handful of
    infrastructure events and the tasks themselves may be fine. Scoring a window that contains a
    fleet-wide outage measures the outage, not the fleet — so name those dates explicitly and show
    what the rates look like without them."""
    n = {}
    for r in rows:
        if r.get("status") != "MEASURED":
            continue
        for d in (r.get("dark_dates") or []):
            n[d] = n.get(d, 0) + 1
    return {d: c for d, c in n.items() if c >= FLEET_EVENT_MIN}, n


def adjusted(r, events):
    """(rate, expected) with fleet-event dates removed from the denominator."""
    shared = sum(1 for d in (r.get("dark_dates") or []) if d in events)
    exp = (r.get("expected") or 0) - shared
    if exp <= 0:
        return None, 0, shared
    return round(100.0 * r.get("hit", 0) / exp, 1), exp, shared


def main():
    p = sys.argv[sys.argv.index("--json") + 1] if "--json" in sys.argv else os.path.join(OS_DIR, "fleet/audit.json")
    rows = json.load(open(p))
    events, allmiss = fleet_events(rows)
    if events:
        tot = sum(allmiss.values()) or 1
        share = sum(events.values())
        print("# Correlated fleet events — READ THIS BEFORE THE VERDICTS\n")
        print("%d of %d recorded misses (%.0f%%) fall on %d dates where %d+ unrelated tasks missed\n"
              "at once. Those are infrastructure events, not task defects. A task's rate below is\n"
              "dragged down by every one of them.\n" % (share, tot, 100.0 * share / tot, len(events), FLEET_EVENT_MIN))
        print("| Date | Tasks that missed |")
        print("|---|---:|")
        for d, c in sorted(events.items(), key=lambda x: -x[1]):
            print("| %s | %d |" % (d, c))
        print("\n| Task | Rate as measured | Rate excluding fleet events | Shared-event misses |")
        print("|---|---:|---:|---:|")
        for r in sorted((x for x in rows if x.get("status") == "MEASURED"),
                        key=lambda x: (x.get("rate") if x.get("rate") is not None else 999)):
            ar, aexp, shared = adjusted(r, events)
            if not shared:
                continue
            print("| %s | %s%% | %s | %d of %d misses |" % (
                r["task"], r.get("rate"), ("%.1f%% (of %d)" % (ar, aexp)) if ar is not None else "no instances left",
                shared, r.get("miss", 0)))
        print()

    out = {"GO": [], "REMEDIATE": [], "RETIRE": [], "NO EVIDENCE": []}
    for r in rows:
        v, why = verdict(r)
        out[v].append((r, why))
    total = len(rows)
    print("# Fleet gate — keep / fix / kill (%d Tier-1 publications)\n" % total)
    print("Gate: >=%.0f%% delivery, <=%d consecutive misses, 0 accuracy incidents, verifiable, testable.\n"
          % (RATE_FLOOR, DARK_CEILING))
    print("| Verdict | Count | Share |")
    print("|---|---:|---:|")
    for v in ("GO", "REMEDIATE", "RETIRE", "NO EVIDENCE"):
        print("| %s | %d | %.0f%% |" % (v, len(out[v]), 100.0 * len(out[v]) / total if total else 0))

    for v, head in (("RETIRE", "Never delivered since inception — retire or rebuild deliberately"),
                    ("REMEDIATE", "Delivers, but not reliably enough to trust unattended"),
                    ("GO", "Meets the gate — leave alone"),
                    ("NO EVIDENCE", "Cannot be judged yet — NOT a failure")):
        if not out[v]:
            continue
        print("\n## %s (%d) — %s\n" % (v, len(out[v]), head))
        if v in ("RETIRE", "REMEDIATE"):
            print("| Task | Cadence | Rate | Delivered | Defect class | Why it failed the gate |")
            print("|---|---|---:|---|---|---|")
            for r, why in sorted(out[v], key=lambda x: (x[0].get("rate") if x[0].get("rate") is not None else -1)):
                print("| %s | %s | %s%% | %d/%d | %s | %s |" % (
                    r["task"], r.get("cadence", ""),
                    r.get("rate") if r.get("rate") is not None else "—",
                    r.get("hit", 0), r.get("expected", 0), shape(r), why))
        else:
            for r, why in sorted(out[v], key=lambda x: x[0]["task"]):
                print("- **%s** — %s" % (r["task"], why))
    print("\n---\nRETIRE is the finding that matters most: a task nobody receives and nobody misses "
          "has been costing a scheduled run for nothing. REMEDIATE items are sorted worst-first and "
          "grouped by defect class, because the class decides the fix — an OUTAGE is one "
          "infrastructure repair covering many tasks, FLAKY is per-task work.")


if __name__ == "__main__":
    main()
