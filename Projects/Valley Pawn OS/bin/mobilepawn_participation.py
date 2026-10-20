#!/usr/bin/env python3
"""mobilepawn_participation.py [YYYY-MM] [--render] [--no-pull] — native `monthly-mobilepawn-participation`
(1st–3rd of month 09:15 ET, posts exactly once; Mac-first wave 3, 2026-10-19). The SKILL's steps verbatim:
  STEP 1  already posted?  <MPP>/out/<YM>/POSTED.txt (or a sent outbox receipt this month) -> stop
  STEP 2  python3 bin/mobilepawn_monthly.py <YM> <MPP>/out/<YM>   exit 0 = post verbatim, exit 2 = HOLD
  STEP 3  self-heal a HOLD: on the 1st re-run every 10 min for up to 60 min, then one ledger row;
          on the 2nd/3rd pull what HOLD.txt names (end-of-month cell, bin/bravo_pull.sh, one trigger per
          window), re-run STEP 2 once, else one ledger row (the 3rd is the last automatic try)
  STEP 4  post slack_post.txt VERBATIM to #mobilepawn-participation (C0C55HRGPBP) as the ops bot,
          then write POSTED.txt. Publish guard + receipt live inside vp_slack.py.
--render: formatter only, prints the post, pulls nothing, writes nothing under out/ except the formatter's own files
in fleet/test_output/.
"""
import calendar
import datetime as dt
import glob
import os
import re
import subprocess
import sys
import time
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
OS_DIR = os.path.dirname(HERE)
PROJ = os.path.dirname(OS_DIR)
AGENT = "monthly-mobilepawn-participation"
ET = ZoneInfo("America/New_York")
MPP = os.path.join(PROJ, "MobilePawn Participation")
LEDGER = os.path.join(OS_DIR, "fleet", "FAILURE_LEDGER.md")
CH = "C0C55HRGPBP"
PY = sys.executable or "/usr/bin/python3"
STORES = ["CUL", "HAR", "LEX", "ROA", "WAY"]


def ledger(sentence):
    try:
        open(LEDGER, "a").write("| %s (native) | %s | %s | NEEDS_HUMAN: no | OPEN |\n"
                                % (dt.datetime.now(ET).strftime("%Y-%m-%d %H:%M ET"), AGENT, sentence))
    except OSError:
        pass


def compile_(ym, out):
    p = subprocess.run([PY, os.path.join(HERE, "mobilepawn_monthly.py"), ym, out], capture_output=True, text=True, timeout=600)
    return p.returncode, p.stdout, p.stderr


def missing_from_hold(out):
    """HOLD.txt lines: 'CUL 2026-09: ...' or 'CUL 2025-09 (year-ago): ...' -> {month: [stores]}"""
    need = {}
    try:
        for line in open(os.path.join(out, "HOLD.txt")):
            m = re.match(r"^(CUL|HAR|LEX|ROA|WAY) (\d{4}-\d{2})", line.strip())
            if m:
                need.setdefault(m.group(2), []).append(m.group(1))
    except OSError:
        pass
    return need


def pull_missing(need):
    for ym, stores in need.items():
        y, m = map(int, ym.split("-"))
        start, end = dt.date(y, m, 1), dt.date(y, m, calendar.monthrange(y, m)[1])
        subprocess.run(["/bin/bash", os.path.join(HERE, "bravo_pull.sh"), "end-of-month", "%s..%s" % (start, end),
                        ",".join(stores), "mobilepawn-%s-%d" % (ym, int(time.time()))], capture_output=True, text=True, timeout=7500)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    render, no_pull = "--render" in sys.argv, "--no-pull" in sys.argv
    today = dt.datetime.now(ET).date()
    if args:
        ym = args[0]
    else:
        ym = (today.replace(day=1) - dt.timedelta(days=1)).strftime("%Y-%m")
    out = os.path.join(OS_DIR, "fleet", "test_output", "mobilepawn_render", ym + "-" + dt.datetime.now(ET).strftime("%H%M%S")) if render else os.path.join(MPP, "out", ym)
    os.makedirs(out, exist_ok=True)
    posted = os.path.join(MPP, "out", ym, "POSTED.txt")
    if not render:
        if os.path.exists(posted):
            print("already posted", ym); return 0
        first = dt.datetime.combine(today.replace(day=1), dt.time()).timestamp()
        sent = [p for p in glob.glob(os.path.join(OS_DIR, "fleet", "outbox", "sent", "monthly-mobilepawn-participation-*")) if os.path.getmtime(p) >= first]
        if sent:
            open(posted, "w").write("%s (outbox) seen %s\n" % (os.path.basename(sent[0]), dt.datetime.now(ET).isoformat()))
            print("already posted via outbox", ym); return 0
    rc, post, err = compile_(ym, out)
    if rc == 2 and not render and not no_pull:
        if today.day == 1:
            for _ in range(6):
                time.sleep(600)
                rc, post, err = compile_(ym, out)
                if rc == 0:
                    break
            if rc != 0:
                ledger("MobilePawn participation report held — month-end numbers not on file yet; will retry tomorrow.")
                print("HOLD (day 1) — retry tomorrow"); return 2
        else:
            need = missing_from_hold(out)
            if need:
                pull_missing(need)
                rc, post, err = compile_(ym, out)
            if rc != 0:
                ledger("MobilePawn participation report held — month-end numbers could not be pulled.")
                print("HOLD (day %d) — %s" % (today.day, open(os.path.join(out, "HOLD.txt")).read().strip()[:300] if os.path.exists(os.path.join(out, "HOLD.txt")) else err.strip()[:300])); return 2
    if rc != 0:
        print("HOLD — %s" % (open(os.path.join(out, "HOLD.txt")).read().strip() if os.path.exists(os.path.join(out, "HOLD.txt")) else err.strip()))
        return 2
    if render:
        print("=== RENDER ONLY ===\n" + post); return 0
    pf = os.path.join(out, "slack_post.txt")
    if not os.path.exists(pf):
        open(pf, "w").write(post)
    p = subprocess.run([PY, os.path.join(HERE, "vp_slack.py"), "post", CH, "--file", pf], capture_output=True, text=True,
                       timeout=60, env=dict(os.environ, VP_TASK=AGENT))
    if p.returncode != 0:
        ledger("MobilePawn participation report for %s was built but did not post." % ym)
        print("post failed:", p.stderr.strip()[:200]); return 1
    if "DRY RUN" in p.stdout:
        print(p.stdout.strip()); return 0
    open(posted, "w").write("native %s ts=%s\n" % (dt.datetime.now(ET).isoformat(), p.stdout.strip()))
    print("posted", ym)
    return 0


if __name__ == "__main__":
    sys.exit(main())
