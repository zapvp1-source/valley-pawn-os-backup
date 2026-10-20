#!/usr/bin/env python3
"""task_lastrun.py — read-only: for each ENABLED scheduled task, print id, cron/fireAt, and
lastRunAt (both raw and as an ISO UTC string), so a guardian pass can compute missed fires
without guessing. Added 2026-10-19 (21:45 ET guardian pass) because task_preflight.py predicts
failure WALLS, not missed runs, and reg_shape.py only prints registry structure — neither gives
lastRunAt per task. Read-only, mirrors reg_shape.py's path-discovery pattern (glob, not a
hardcoded session id, so it survives a session-id change).

    task_lastrun.py            all enabled tasks
    task_lastrun.py --all      all tasks, enabled or not
"""
import glob
import json
import os
import sys
from datetime import datetime, timezone

HOME = os.path.expanduser("~")
REG_GLOB = os.path.join(HOME, "Library/Application Support/Claude/local-agent-mode-sessions/*/*/scheduled-tasks.json")


def load_registry():
    paths = sorted(glob.glob(REG_GLOB), key=os.path.getmtime, reverse=True)
    if not paths:
        sys.exit("registry not found")
    return json.load(open(paths[0]))["scheduledTasks"]


def fmt_ts(v):
    if v is None:
        return "None"
    try:
        if isinstance(v, (int, float)) or (isinstance(v, str) and v.isdigit()):
            ms = float(v)
            if ms > 1e12:
                dt = datetime.fromtimestamp(ms / 1000.0, tz=timezone.utc)
            else:
                dt = datetime.fromtimestamp(ms, tz=timezone.utc)
            return dt.isoformat()
        return str(v)
    except Exception as e:
        return "RAW:%r (err=%s)" % (v, e)


def main():
    show_all = "--all" in sys.argv
    reg = load_registry()
    rows = []
    for t in reg:
        if not show_all and not t.get("enabled"):
            continue
        rows.append(t)
    rows.sort(key=lambda t: t.get("id", ""))
    for t in rows:
        tid = os.path.basename(os.path.dirname(t.get("filePath", "") or "")) or t.get("id", "?")
        print("%-46s enabled=%-5s cron=%-28s lastRunAt_raw=%-16s lastRunAt_utc=%s" % (
            tid[:46], bool(t.get("enabled")),
            str(t.get("cronExpression") or t.get("fireAt") or "")[:28],
            str(t.get("lastRunAt")), fmt_ts(t.get("lastRunAt"))))
    print("TOTAL rows=%d" % len(rows))


if __name__ == "__main__":
    main()
