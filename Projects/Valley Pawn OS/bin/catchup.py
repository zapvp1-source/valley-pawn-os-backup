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
if wd == 6:   # Sunday — forfeited-loan win-back list build (feeds Tuesday email + Thursday texts); added 2026-10-05
    JOBS.append(("com.valleypawn.forfeiture-winback", "forfeiture_winback_weekly.sh", at(12, 30), at(23, 0),
                 lambda s: os.path.isdir(os.path.join(HOME, "Documents/Claude/Projects/Email Refinement/forfeiture_winback/runs", today.isoformat()))))
# Weekly Mac maintenance (Sun 04:45). Added 2026-10-06: the Mac was off Sun 10/4, the run was skipped
# and nothing would have run it until 10/11 (fleet-doctor flagged mac_maintenance.log quiet). Unlike the
# same-day jobs above, this one stays useful all week, so the window is the rest of the week. Evidence =
# its own log written since the slot. It only thins TM local snapshots, deletes age-gated temp files and
# DMs Joshua one health line — nothing customer-facing.
mm_slot = at(4, 45, sunday)
JOBS.append(("com.valleypawn.mac-maintenance", "mac_weekly_maintenance.py", mm_slot, at(23, 0, sunday + dt.timedelta(days=6)),
             lambda s: file_since(LOGF("mac_maintenance"), s)))
if wd == 0:   # Monday
    JOBS.append(("com.valleypawn.monday-compile", "monday_compile.py", at(8, 45), at(14, 0),
                 lambda s: receipt_since("monday-bravo-combined-compile", s) or file_since(LOGF("monday-compile"), s)))
    JOBS.append(("com.valleypawn.loan-layaway-dms", "loan_layaway_dms.py", at(9, 0), at(14, 0),
                 lambda s: receipt_since("weekly-loan-layaway-manager-dms", s) or file_since(LOGF("weekly-loan-layaway-manager-dms"), s)))
    # weekly canvases + layaway yield (native 2026-10-06); each run is re-run safe (same content = no-op)
    for label, kind, task, h, m in [("com.valleypawn.loan-canvas", "loan", "weekly-loan-review-canvas-refresh", 9, 20),
                                    ("com.valleypawn.layaway-canvas", "layaway", "weekly-layaway-review-canvas-refresh", 9, 22),
                                    ("com.valleypawn.employee-canvas", "employee", "weekly-employee-perf-canvas-refresh", 9, 24),
                                    ("com.valleypawn.aged-canvas", "aged", "weekly-aged-inventory-canvas-refresh", 9, 26),
                                    ("com.valleypawn.store-canvas", "store", "weekly-store-perf-canvas-refresh", 9, 28)]:
        JOBS.append((label, "weekly_canvases.py " + kind, at(h, m), at(14, 0),
                     (lambda t: lambda s: receipt_since(t, s) or file_since(LOGF(t), s))(task)))
    JOBS.append(("com.valleypawn.layaway-yield-weekly", "layaway_yield_weekly.py", at(11, 15), at(16, 0),
                 lambda s: receipt_since("layaway-yield-weekly", s) or file_since(LOGF("layaway-yield-weekly"), s)))

# Mac-first wave 1 (2026-10-08): native replacements of Cowork tasks. Each agent is DORMANT until
# fleet/state/native_live/<task> exists (bin/vp_live.sh), so kickstarting a dormant one is a silent no-op.
# Evidence = a receipt under the task's own name (vp_slack writes it) or the job's own state/output.
CU = os.path.join(OS_DIR, "fleet/state/chekkit_unanswered")
if wd != 6:   # Mon-Sat
    yday = today - dt.timedelta(days=1)
    JOBS.append(("com.valleypawn.chekkit-unanswered-alert", "chekkit_unanswered.py morning", at(8, 0), at(12, 0),
                 lambda s: receipt_since("chekkit-unanswered-alert", s) or os.path.exists(os.path.join(CU, "morning-%s.json" % yday))))
    JOBS.append(("com.valleypawn.chekkit-unanswered-eod", "chekkit_unanswered.py eod", at(19, 0), at(23, 0),
                 lambda s: receipt_since("chekkit-unanswered-eod-followup", s) or os.path.exists(os.path.join(CU, "eod-%s.json" % today))))
    JOBS.append(("com.valleypawn.daily-audit-digest", "daily_audit_send.py", at(9, 40), at(18, 0),
                 lambda s: receipt_since("daily-store-audit-digest", s) or file_since(os.path.join(OS_DIR, "daily-audit", "*.sent"), s)))
SHOP_RES = os.path.join(HOME, "Documents/Claude/Projects/Website/analytics/data/shop/result.json")
for h, until in ((7, at(14, 50)), (15, at(23, 0))):
    JOBS.append(("com.valleypawn.shop-refresh", "shop_refresh.py", at(h, 0), until,
                 lambda s: file_since(SHOP_RES, s)))
if wd == 0:   # Monday deal-of-the-week prompt (useful until the 11:00 reminder) and reminder (until the noon cutoff)
    JOBS.append(("com.valleypawn.deal-of-week-prompt", "deal_of_week_monday.py prompt", at(8, 10), at(11, 0),
                 lambda s: receipt_since("vp-deal-of-week-monday-prompt", s) or file_since(LOGF("vp-deal-of-week-monday-prompt"), s)))
    JOBS.append(("com.valleypawn.deal-of-week-reminder", "deal_of_week_monday.py reminder", at(11, 0), at(11, 50),
                 lambda s: receipt_since("vp-deal-of-week-monday-reminder", s) or file_since(LOGF("vp-deal-of-week-monday-reminder"), s)))


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
