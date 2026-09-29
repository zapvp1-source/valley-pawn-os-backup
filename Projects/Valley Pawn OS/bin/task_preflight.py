#!/usr/bin/env python3
"""task_preflight.py — predict, before a task is switched on, which of the fleet's KNOWN failure walls
it will hit in an unattended scheduled run. Read-only. Runs on the host (needs the registry + SKILLs).

Every failure since 9/16 has been one of these, and each is visible statically:
  MAC      the SKILL relies on Control_your_Mac / osascript / iMessage connectors — absent in scheduled
           sessions (proven 9/21, 9/25). Fix: native agent, or a file bridge (outbox, sms relay).
  SEND     the SKILL calls slack_send_message but the task has no stored approval for it and no
           OUTBOX step — the send is auto-declined (jewelry 9/23, chekkit-eod 9/21, northwest 9/26).
  BROWSER  the SKILL drives Chrome / the browser pane but the task is not in skip-permission mode —
           a site-access card appears with no one to click it (guesty, GA4, chekkit, slack web).
  TOOL     the SKILL names an MCP tool (mcp__<server>__<tool>) the task has no stored approval for —
           the run stalls mid-flow (precious-metals 9/24, roster-refresh, northwest Drive).

  task_preflight.py                 table for every task + SUMMARY
  task_preflight.py --disabled      only disabled tasks (the parked fleet)
  task_preflight.py --task <id>     one task, with the evidence lines
  task_preflight.py --json <path>   also write machine-readable results
"""
import glob
import json
import os
import re
import sys

HOME = os.path.expanduser("~")
SCHED = os.path.join(HOME, "Documents/Claude/Scheduled")
REG_GLOB = os.path.join(HOME, "Library/Application Support/Claude/local-agent-mode-sessions/*/*/scheduled-tasks.json")

MAC_RX = re.compile(r"mcp__Control_your_Mac__|Read_and_Send_iMessages|do shell script", re.I)
SEND_RX = re.compile(r"slack_send_message")
OUTBOX_MARK = "OUTBOX SEND (MANDATORY)"
BROWSER_RX = re.compile(r"mcp__claude-in-chrome__|mcp__Claude_Browser__|claude in chrome|browser pane", re.I)
TOOL_RX = re.compile(r"mcp__([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})__([A-Za-z0-9_\-]+)")
# a SKILL that says it must NOT use the connector / uses the native path instead is not a MAC wall
MAC_NEGATED = re.compile(r"(do not|don't|never)\s+(call|use|load)[^.\n]{0,60}(Control_your_Mac|osascript|iMessage)", re.I)


LEDGER = os.path.join(HOME, "Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md")
MAC_EVIDENCE = re.compile(r"Control_your_Mac|osascript|local[- ]Mac bridge|LOCAL ACCESS GATE FAILED|no .{0,20}Mac access|iMessages? (tool|connector)", re.I)


def mac_ledger(days=14):
    import datetime as dt
    cut = (dt.date.today() - dt.timedelta(days=days)).isoformat()
    out = {}
    try:
        for line in open(LEDGER, errors="replace"):
            if not line.startswith("| 20"):
                continue
            cells = [c.strip() for c in line.split("|")]
            if len(cells) < 4 or cells[1][:10] < cut:
                continue
            if MAC_EVIDENCE.search(cells[3]) and "RECOVERED" not in line and "FIXED" not in line:
                for t in re.split(r"[,/ ]+", cells[2]):
                    if t and t[0].isalpha():
                        out.setdefault(t.strip(), []).append(cells[1] + ": " + cells[3][:140])
    except OSError:
        pass
    return out


MAC_LEDGER = mac_ledger()


def load_registry():
    paths = sorted(glob.glob(REG_GLOB), key=os.path.getmtime, reverse=True)
    if not paths:
        sys.exit("registry not found")
    return json.load(open(paths[0]))["scheduledTasks"]


def scan(task):
    tid = task["id"]
    p = os.path.join(SCHED, tid, "SKILL.md")
    if not os.path.isfile(p):
        return None
    body = open(p, errors="replace").read()
    approved = {a.get("toolName", "") for a in (task.get("approvedPermissions") or [])}
    walls, ev = [], {}
    # MAC is judged from RUN EVIDENCE, not SKILL text: nearly every SKILL carries a banner telling it to
    # use osascript, yet most of them run fine through the session's own file mount (verified 9/28 —
    # items-to-price, cloudcover, funds-verification all "matched" the text and all post daily). A task
    # only has a MAC wall if one of its own runs in the last 14 days wrote a ledger row saying so.
    hits = MAC_LEDGER.get(tid)
    if hits:
        walls.append("MAC"); ev["MAC"] = hits[:2]
    if SEND_RX.search(body) and OUTBOX_MARK not in body:
        send_ok = any(a.endswith("__slack_send_message") for a in approved)
        if not send_ok:
            walls.append("SEND"); ev["SEND"] = ["no stored slack_send_message approval, no outbox step"]
    if BROWSER_RX.search(body):
        mode = task.get("chromePermissionMode")
        if mode != "skip_all_permission_checks":
            walls.append("BROWSER"); ev["BROWSER"] = ["chromePermissionMode=%s allowed=%s" % (mode, task.get("chromeAllowedDomains"))]
    missing = sorted({"mcp__%s__%s" % m for m in TOOL_RX.findall(body)} - approved)
    # slack_send_message is judged above; don't double-count it
    missing = [m for m in missing if not m.endswith("__slack_send_message")]
    if missing:
        walls.append("TOOL"); ev["TOOL"] = missing[:6]
    return {"id": tid, "enabled": bool(task.get("enabled")), "walls": walls, "evidence": ev,
            "cron": task.get("cronExpression") or task.get("fireAt"), "approved": len(approved)}


def main():
    only_disabled = "--disabled" in sys.argv
    one = sys.argv[sys.argv.index("--task") + 1] if "--task" in sys.argv else None
    reg = load_registry()
    rows = []
    for t in reg:
        if one and t["id"] != one:
            continue
        if only_disabled and t.get("enabled"):
            continue
        r = scan(t)
        if r:
            rows.append(r)
    rows.sort(key=lambda r: (not r["enabled"], -len(r["walls"]), r["id"]))
    for r in rows:
        print("%-44s %-3s %-22s %s" % (r["id"][:44], "ON" if r["enabled"] else "off",
                                        ",".join(r["walls"]) or "clear", r["cron"] or ""))
        if one:
            for k, v in r["evidence"].items():
                for line in v:
                    print("    %s: %s" % (k, line.strip()[:200]))
    def count(pred):
        return sum(1 for r in rows if pred(r))
    for scope, pred in (("enabled", lambda r: r["enabled"]), ("disabled", lambda r: not r["enabled"])):
        rs = [r for r in rows if pred(r)]
        if not rs:
            continue
        print("SUMMARY %s total=%d clear=%d mac=%d send=%d browser=%d tool=%d" % (
            scope, len(rs), sum(1 for r in rs if not r["walls"]),
            sum("MAC" in r["walls"] for r in rs), sum("SEND" in r["walls"] for r in rs),
            sum("BROWSER" in r["walls"] for r in rs), sum("TOOL" in r["walls"] for r in rs)))
    if "--json" in sys.argv:
        json.dump(rows, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1)


if __name__ == "__main__":
    main()
