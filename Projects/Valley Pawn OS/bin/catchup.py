#!/usr/bin/env python3
"""catchup.py [--render] — run any critical native job whose scheduled time passed while the Mac was off.

WHY (2026-10-04): the Mac was down Sat 12:11 -> Sun 13:03 and again Sun 15:36 -> 17:05. launchd does not
run a StartCalendarInterval job that came due while the machine was powered off, so the Sunday 16:30
Monday pull, the Sunday daily reports, backups, Oura and health capture were all silently skipped.
This runs at load (boot/login) and every 15 minutes: for each job below, if its slot has passed today,
we are still inside its useful window, there is no evidence it ran since the slot, and it is not
running now, it kickstarts the job's own launchd agent. The job itself still does all its own checks
(completeness gates, de-duplication, publish guard) — this only makes sure it gets its turn.
Evidence = a receipt (fleet/receipts/<task>.jsonl) or the job's own output file, never a run record.
"""
import datetime as dt
import glob
import json
import os
import subprocess
import sys

HOME = os.path.expanduser("~")
OS_DIR = os.path.join(HOME, "Documents/Claude/Projects/Valley Pawn OS")
BRAVO = os.path.join(HOME, "Documents/Claude/Projects/Bravo Data Extraction")
REC = os.path.join(OS_DIR, "fleet/receipts")
LOG = os.path.join(HOME, "Library/Logs/valleypawn/catchup.log")
now = dt.datetime.now()
today = now.date()


def receipt_since(task, since):
    p = os.path.join(REC, task + ".jsonl")
    try:
        for line in open(p):
            r = json.loads(line)
            if r.get("ok", True) and dt.datetime.fromisoformat(r["ts"][:19]) >= since:
                return True
    except (OSError, ValueError, KeyError):
        pass
    return False


def file_since(pattern, since):
    return any(dt.datetime.fromtimestamp(os.path.getmtime(p)) >= since for p in glob.glob(pattern))


def running(pattern):
    return subprocess.run(["pgrep", "-f", pattern], capture_output=True).returncode == 0


def LOGF(agent):
    return os.path.join(HOME, "Library/Logs/valleypawn/%s.log" % agent)


def at(h, m, day=None):
    return dt.datetime.combine(day or today, dt.time(h, m))


# (label, script-pattern-for-pgrep, slot datetime or None if not due today, window-end, evidence fn)
wd = today.weekday()  # Mon=0 .. Sun=6
sunday = today - dt.timedelta(days=(wd + 1) % 7)   # most recent Sunday (today if Sunday)
JOBS = []
# Monday pull: due Sun 16:30, still useful until Mon 07:30 (the 08:00/08:45 reports read it)
mp_slot = at(16, 30, sunday)
if (wd == 6 and now >= mp_slot) or (wd == 0 and now < at(7, 30)):
    cert_dates = [sunday.isoformat(), today.isoformat()]
    JOBS.append(("com.valleypawn.monday-pull", "monday_pull.sh", mp_slot, at(7, 30, sunday + dt.timedelta(days=1)),
                 lambda s: any(os.path.exists(os.path.join(BRAVO, "logs", "_monday_pull_status_%s.txt" % d)) for d in cert_dates)))
# daily morning reports (they decide themselves whether yesterday needs a post)
for label, task, h, m in [("com.valleypawn.daily-report-pawn", "daily-report-pawn", 7, 15),
                          ("com.valleypawn.daily-report-sold", "daily-report-sold", 7, 45),
                          ("com.valleypawn.daily-report-discount", "daily-report-discount", 8, 25)]:
    JOBS.append((label, "daily_report.sh " + task.split("-")[-1], at(h, m), at(20, 0),
                 (lambda t: lambda s: receipt_since(t, s) or file_since(LOGF(t), s))(task)))
for label, task, h, m in [("com.valleypawn.backup-health", "backup-health-watchdog", 7, 0),
                          ("com.valleypawn.oura-import-check", "oura-daily-import", 8, 30),
                          ("com.valleypawn.health-episode", "health-episode-capture", 9, 15)]:
    JOBS.append((label, task.replace("-watchdog", "").replace("-capture", ""), at(h, m), at(22, 0),
                 (lambda t: lambda s: receipt_since(t, s) or file_since(LOGF(t), s))(task)))
JOBS.append(("com.valleypawn.funds-verification", "funds_verification.py", at(18, 30), at(23, 30),
             lambda s: os.path.exists(os.path.join(HOME, "Documents/Claude/Projects/Daily Funds Verification/%s Funds Verification.md" % today))
             or file_since(LOGF("daily-funds-verification"), s)))
if wd == 0:   # Monday
    JOBS.append(("com.valleypawn.monday-compile", "monday_compile.py", at(8, 45), at(14, 0),
                 lambda s: receipt_since("monday-bravo-combined-compile", s) or file_since(LOGF("monday-compile"), s)))
    JOBS.append(("com.valleypawn.loan-layaway-dms", "loan_layaway_dms.py", at(9, 0), at(14, 0),
                 lambda s: receipt_since("weekly-loan-layaway-manager-dms", s) or file_since(LOGF("weekly-loan-layaway-manager-dms"), s)))


def main():
    render = "--render" in sys.argv
    uid = os.getuid()
    fired = []
    for label, pat, slot, until, done in JOBS:
        if not (slot <= now <= until):
            continue
        if done(slot) or running(pat):
            continue
        if not os.path.exists(os.path.join(HOME, "Library/LaunchAgents", label + ".plist")):
            continue
        fired.append(label)
        if not render:
            subprocess.run(["launchctl", "kickstart", "gui/%d/%s" % (uid, label)], capture_output=True)
    line = "%s %s %s" % (now.strftime("%Y-%m-%d %H:%M"), "WOULD FIRE" if render else "fired", ", ".join(fired) or "nothing due")
    print(line)
    if not render and fired:
        os.makedirs(os.path.dirname(LOG), exist_ok=True)
        open(LOG, "a").write(line + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
