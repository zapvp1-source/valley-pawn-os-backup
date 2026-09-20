#!/usr/bin/env python3
"""audit_spotcheck.py — for a task the audit calls dark, ask what was ACTUALLY in the channel.

WHY (2026-09-19): the audit counts a miss when it cannot find its MARKER inside the window. That is
two different failures wearing one face:

  TRULY DARK        — nothing was posted at all. A real miss, and a real repair.
  MARKER MISSED     — something WAS posted, the marker just did not match it (wording drifted, the
                      report changed shape, the marker was written from a different example).

Treating the second as the first produces a repair list full of tasks that are working, and that is
not hypothetical here: a three-day "pawn-walk is posting empty messages" defect turned out to be a
reading artifact, and the whole 11-task daily repair list was built before that was known. Before
anyone spends a day fixing a task, check which kind of miss it actually is.

Reads with the vp_ops_engine bot's OWN token — the app that posts these — because a Cowork-connector
read cannot see another app's message text (that is what caused the phantom defect).

    audit_spotcheck.py <task> [--max 6]
"""
import datetime as dt
import json
import os
import sys

OS_DIR = os.path.expanduser("~/Documents/Claude/Projects/Valley Pawn OS")
sys.path.insert(0, os.path.join(OS_DIR, "bin"))
import vp_slack                                    # the posting app's own token + history call

MANIFEST = os.path.join(OS_DIR, "fleet/expected_outputs.json")
AUDIT = os.path.join(OS_DIR, "fleet/audit.json")


def hhmm(cadence):
    for tok in cadence.replace("-", " ").split():
        if tok.endswith("et") and tok[:-2].isdigit() and len(tok) == 6:
            return int(tok[:2]), int(tok[2:4])
    return 8, 0


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 2
    task = args[0]
    mx = int(sys.argv[sys.argv.index("--max") + 1]) if "--max" in sys.argv else 6

    ALL = json.load(open(MANIFEST))["entries"]
    entries = [e for e in ALL if e.get("task") == task]
    rows = [r for r in json.load(open(AUDIT)) if r.get("task") == task]
    if not entries or not rows:
        print("no manifest entry or audit row for %s" % task)
        return 1
    e, r = entries[0], rows[0]
    ch, marker = e.get("channel_id"), (e.get("marker") or "")
    if not ch:
        print("%s does not publish to a readable channel (output=%s) — nothing to spot-check"
              % (task, e.get("output")))
        return 1
    dark = (r.get("dark_dates") or [])[-mx:]
    if not dark:
        print("%s has no recorded dark dates — nothing to check" % task)
        return 0

    hh, mm = hhmm(e.get("cadence", ""))
    grace = e.get("grace_hours", 4)
    year = dt.datetime.now().year
    print("# Spot-check: %s\n" % task)
    print("Marker the audit looks for: %r · window: %02d:%02d + %sh grace\n" % (marker, hh, mm, grace))
    print("| Date | Publisher msgs in window | Marker found | Verdict |")
    print("|---|---:|---|---|")
    truly_dark = marker_missed = 0
    samples = []
    for md in dark:
        m, d = md.split("/")
        start = dt.datetime(year, int(m), int(d), hh, mm)
        end = start + dt.timedelta(hours=max(grace, 1))
        try:
            res = vp_slack.call("conversations.history", params={
                "channel": ch, "oldest": str(start.timestamp()),
                "latest": str(end.timestamp()), "limit": 50})
            msgs = res.get("messages", []) if res.get("ok") else []
            err = None if res.get("ok") else res.get("error")
        except Exception as ex:
            msgs, err = [], str(ex)[:60]
        if err:
            print("| %s | ? | ? | could not read: %s |" % (md, err))
            continue
        # Only the PUBLISHER's messages count. The first version counted any traffic in the
        # channel, so a day when Joshua said "Thanks man!" in #general read as "something was
        # posted, the marker just missed" — which would send someone off to fix a marker on a task
        # that genuinely did not run. #general and #pawn-walks carry human conversation; a report
        # is only evidence of itself.
        pub = [x for x in msgs
               if x.get("bot_id") or x.get("user") == "U0BLQTHLUTA"
               or "Sent using" in (x.get("text") or "")]
        msgs = pub
        hit = any(marker in (x.get("text") or "") for x in msgs) if marker else False
        if not msgs:
            verdict = "**TRULY DARK** — publisher posted nothing"
            truly_dark += 1
        elif hit:
            verdict = "marker present — audit should not have called this dark (check window)"
        else:
            # A shared channel (#general carries cloudcover, dress-code AND clock-in) means the
            # publisher posting "something" proves nothing about THIS task. Name the sibling report
            # explicitly rather than implying the marker drifted — that distinction decides whether
            # someone spends the day fixing a marker or fixing a task.
            blob = " ".join((x.get("text") or "") for x in msgs)
            sib = sorted({o["task"] for o in ALL
                          if o.get("task") != task and o.get("marker")
                          and o.get("channel_id") == ch and o["marker"] in blob})
            if sib:
                verdict = "**STILL DARK** — only a sibling report posted here (%s)" % ", ".join(sib)
                truly_dark += 1
            else:
                verdict = "**MARKER MISSED** — this publisher posted, marker did not match"
                marker_missed += 1
                samples.append((md, (msgs[0].get("text") or "")[:160].replace("\n", " ")))
        print("| %s | %d | %s | %s |" % (md, len(msgs), "yes" if hit else "no", verdict))

    print("\n**%d truly dark · %d posted-but-marker-missed** (of %d checked)."
          % (truly_dark, marker_missed, len(dark)))
    if samples:
        print("\nWhat was actually posted on the marker-missed days — compare against the marker:\n")
        for md, s in samples[:4]:
            print("- **%s** — %s" % (md, s))
        print("\nIf these are real reports, the fix is the MARKER, not the task. Correct it in")
        print("expected_outputs.json against a real post (additive, with a dated _corrected note).")
    if truly_dark and not marker_missed:
        print("\nEvery miss checked was a real absence. This task's repair is genuine work.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
