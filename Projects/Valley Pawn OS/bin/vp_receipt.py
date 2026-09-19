#!/usr/bin/env python3
"""vp_receipt.py — the publication receipt.

WHY THIS EXISTS (2026-09-18)
A publication that lands only in Joshua's DM, or in a Slack canvas, cannot be audited: the ops bot
cannot read another app's DM, so "it ran and delivered" and "it never ran" look exactly the same
from outside. 45% of Tier-1 publications were unmeasurable for that reason alone, which is why the
fleet could be measured at ~62% median delivery and nobody could say which half was real.

A receipt fixes that at the source instead of guessing from the outside: whenever a task publishes
ANYTHING, it appends one line saying what it sent, where, and when. The receipt is local, cheap,
append-only, and independent of the surface — so the audit scores DM tasks, canvas tasks and
channel tasks the same way.

A receipt is evidence of a SEND, not of correctness. It never replaces reading the channel where
the channel is readable; there the channel stays the source of record (Rule 19). It is the
source of record only where no readable surface exists.

    vp_receipt.py write <task> --surface <slack-dm|slack|canvas|file|email> --target <id/path>
                              [--bytes N] [--note "..."] [--ok true|false] [--at ISO8601]
    vp_receipt.py last  <task>              # most recent receipt, human readable
    vp_receipt.py count <task> --since ISO --until ISO

Storage: Valley Pawn OS/fleet/receipts/<task>.jsonl — one JSON object per line, append-only.
Never rewritten, never trimmed by this tool; a receipt that is edited is not evidence.
"""
import argparse
import datetime as dt
import json
import os
import sys

OS_DIR = os.path.expanduser("~/Documents/Claude/Projects/Valley Pawn OS")
RECEIPTS = os.path.join(OS_DIR, "fleet", "receipts")


def _path(task):
    safe = "".join(c for c in task if c.isalnum() or c in "-_.")
    if not safe:
        raise SystemExit("refusing to write a receipt for an unnamed task")
    return os.path.join(RECEIPTS, safe + ".jsonl")


def write(a):
    os.makedirs(RECEIPTS, exist_ok=True)
    ts = a.at or dt.datetime.now().astimezone().isoformat(timespec="seconds")
    rec = {"task": a.task, "ts": ts, "surface": a.surface, "target": a.target,
           "ok": (a.ok != "false"), "bytes": a.bytes, "note": (a.note or "")[:400]}
    with open(_path(a.task), "a") as f:            # append-only, one line, flushed on close
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print("receipt %s %s -> %s%s" % (a.task, ts, a.target, "" if rec["ok"] else "  (FAILED SEND)"))


def _load(task):
    try:
        with open(_path(task)) as f:
            out = []
            for line in f:
                line = line.strip()
                if line:
                    try:
                        out.append(json.loads(line))
                    except ValueError:
                        pass                        # a corrupt line is skipped, never fatal
            return out
    except OSError:
        return []


def last(a):
    rows = _load(a.task)
    if not rows:
        print("no receipts for %s" % a.task)
        return 1
    r = rows[-1]
    print("%s  %s  %s -> %s  %s%s" % (r["task"], r["ts"], r["surface"], r["target"],
                                      "ok" if r.get("ok") else "FAILED",
                                      ("  " + r["note"]) if r.get("note") else ""))
    return 0


def count(a):
    lo, hi = a.since, a.until
    n = sum(1 for r in _load(a.task) if r.get("ok") and lo <= r["ts"][:19] <= hi)
    print(n)
    return 0


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    w = sub.add_parser("write"); w.add_argument("task")
    w.add_argument("--surface", required=True)
    w.add_argument("--target", required=True)
    w.add_argument("--bytes", type=int, default=0)
    w.add_argument("--note", default="")
    w.add_argument("--ok", default="true")
    w.add_argument("--at", default="")
    l = sub.add_parser("last"); l.add_argument("task")
    c = sub.add_parser("count"); c.add_argument("task")
    c.add_argument("--since", required=True); c.add_argument("--until", required=True)
    a = p.parse_args()
    return {"write": write, "last": last, "count": count}[a.cmd](a) or 0


if __name__ == "__main__":
    sys.exit(main())
