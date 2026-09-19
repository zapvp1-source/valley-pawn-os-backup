#!/usr/bin/env python3
"""vp_dryrun.py — the fleet-wide publish guard.

WHY (Joshua, 2026-09-18): "we should be able to test everything and see if it's working in isolation
without publishing a bunch of bullshit to Slack."

Turning this on makes every native publication divert to fleet/test_output/ instead of Slack. The
task runs for real — same data, same compile, same message text — but nothing reaches a channel, a
DM, or a store manager. That is the difference between testing the fleet and rehearsing on your
staff.

THE DANGEROUS FAILURE MODE IS LEAVING IT ON. A guard silently swallowing real publications is worse
than the problem it solves, so it cannot be left on by accident:
  * it ALWAYS carries an expiry (default 2 hours, hard ceiling 24) and is ignored the moment it passes
  * `status` and the fleet audit both announce loudly while it is active
  * a diverted send is NEVER written to the real receipts ledger — it goes to a separate dry-run
    ledger — so an isolation test can never be mistaken for evidence that a task delivered

    vp_dryrun.py on [--minutes N] [--task T ...] [--reason "..."]
    vp_dryrun.py off
    vp_dryrun.py status            # exit 0 = active, 1 = not active
"""
import argparse
import datetime as dt
import json
import os
import sys

OS_DIR = os.path.expanduser("~/Documents/Claude/Projects/Valley Pawn OS")
FLAG = os.path.join(OS_DIR, "fleet", "DRY_RUN.json")
TEST_OUT = os.path.join(OS_DIR, "fleet", "test_output")
MAX_MINUTES = 24 * 60


def _read():
    try:
        with open(FLAG) as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def state():
    """(active, doc). Expiry is enforced on READ, so a forgotten flag disarms itself."""
    d = _read()
    if not d or not d.get("active"):
        return False, d
    try:
        until = dt.datetime.fromisoformat(d["until"])
    except (KeyError, ValueError):
        return False, d                       # a flag without a readable expiry is not a flag
    now = dt.datetime.now(until.tzinfo) if until.tzinfo else dt.datetime.now()
    return (now <= until), d


def active_for(task):
    on, d = state()
    if not on:
        return False
    scope = d.get("scope", "all")
    return scope == "all" or (task or "") in scope


def divert(task, surface, target, text):
    """Write what WOULD have been published, plus a dry-run receipt. Returns the path written."""
    os.makedirs(TEST_OUT, exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    safe = "".join(c for c in (task or "untasked") if c.isalnum() or c in "-_.") or "untasked"
    path = os.path.join(TEST_OUT, "%s-%s-%s.txt" % (safe, surface, stamp))
    with open(path, "w", encoding="utf-8") as f:
        f.write("=== DRY RUN — NOTHING WAS PUBLISHED ===\n")
        f.write("task: %s\nsurface: %s\nwould have gone to: %s\nbytes: %d\nat: %s\n%s\n"
                % (safe, surface, target, len(text.encode()),
                   dt.datetime.now().isoformat(timespec="seconds"), "-" * 60))
        f.write(text)
    with open(os.path.join(TEST_OUT, "dryrun_receipts.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps({"task": safe, "ts": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
                            "surface": surface, "target": target, "dry_run": True,
                            "bytes": len(text.encode()), "file": os.path.basename(path)}) + "\n")
    return path


def cmd_on(a):
    mins = max(1, min(a.minutes, MAX_MINUTES))
    until = dt.datetime.now().astimezone() + dt.timedelta(minutes=mins)
    doc = {"active": True, "until": until.isoformat(timespec="seconds"),
           "scope": a.task or "all", "reason": a.reason or "isolation test",
           "set_at": dt.datetime.now().astimezone().isoformat(timespec="seconds")}
    os.makedirs(os.path.dirname(FLAG), exist_ok=True)
    json.dump(doc, open(FLAG, "w"), indent=1)
    print("DRY RUN ON until %s (%d min) — scope: %s"
          % (until.strftime("%H:%M"), mins, doc["scope"]))
    print("Native publications will divert to fleet/test_output/. Nothing will reach Slack.")
    return 0


def cmd_off(a):
    if os.path.exists(FLAG):
        json.dump({"active": False, "cleared_at": dt.datetime.now().astimezone().isoformat(timespec="seconds")},
                  open(FLAG, "w"), indent=1)
    print("DRY RUN OFF — publications go to Slack normally again.")
    return 0


def cmd_status(a):
    on, d = state()
    if on:
        print("DRY RUN IS ACTIVE until %s — scope: %s — reason: %s"
              % (d.get("until"), d.get("scope"), d.get("reason")))
        print("NOTHING is reaching Slack from native scripts while this is on.")
        return 0
    if d and d.get("active"):
        print("dry run EXPIRED at %s — it is no longer in effect (publications are live)" % d.get("until"))
    else:
        print("dry run is off — publications are live")
    return 1


def main():
    p = argparse.ArgumentParser()
    s = p.add_subparsers(dest="cmd", required=True)
    o = s.add_parser("on")
    o.add_argument("--minutes", type=int, default=120)
    o.add_argument("--task", action="append")
    o.add_argument("--reason", default="")
    s.add_parser("off")
    s.add_parser("status")
    a = p.parse_args()
    return {"on": cmd_on, "off": cmd_off, "status": cmd_status}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
