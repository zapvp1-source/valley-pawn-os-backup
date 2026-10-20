#!/usr/bin/env python3
"""bonus_close_pull.py [YYYY-MM] [--render] [--no-pull] — native `bonus-month-close-pull` (1st of month 11:30 ET;
Mac-first wave 3, 2026-10-19). The SKILL's steps, through the trigger pipeline only, DM to Joshua ONLY:
  3 pull the closed month (bin/bravo_pull.sh, one report per call, serial): end-of-month, chekkit-invites-range,
    employee-activity-range (MONTH-01..LASTDAY, all 5 stores). Gold: the SKILL's full-year scrap-refining-gold pull
    is what TRUNCATED the scrap year files on 10/15 (see scrap_rankings_monthly.py), so here it is (a) skipped when
    the 04:30 scrap-rankings agent already refreshed the year files today, else (b) done the safe way: back up,
    pull P-1..P per store, additive union merge — never a bare full-year pull.
  5 bonus_engine.py collect --month   (holds -> re-drop end-of-month once for the stores it names, collect again)
  6 bonus_engine.py targets --month   (exit 2 = HELD -> ONE plain on-hold sentence to Joshua, stop)
  7 sheet_sync.py --month             (exit 2 = keep step-6 targets and say so; other error = ledger row, continue)
  8 DM: next month's five targets (data/<next>/targets.json, the sheet's numbers), closed-month revenue vs target
    per store (data/history.json vs data/<MONTH>/targets.json), slack_targets.txt in a code block, the SKILL's
    closing line. Never a team channel.
  9 Bonus Program/RUN_LOG.md line.
--render: steps 5-8 against what is on disk (collect/targets/sheet_sync NOT run — they rewrite data files); prints
the DM the live run would send.
"""
import calendar
import datetime as dt
import glob
import json
import os
import shutil
import subprocess
import sys
import time
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
AGENT = "bonus-month-close-pull"
ET = ZoneInfo("America/New_York")
OS_DIR = os.path.dirname(HERE)
PROJ = os.path.dirname(OS_DIR)
BRAVO = os.environ.get("VP_BRAVO_DIR") or os.path.join(PROJ, "Bravo Data Extraction")
BONUS = os.path.join(PROJ, "Bonus Program")
LEDGER = os.path.join(OS_DIR, "fleet", "FAILURE_LEDGER.md")
STORES = ["CUL", "HAR", "ROA", "LEX", "WAY"]
NAMES = {"CUL": "Culpeper", "HAR": "Harrisonburg", "LEX": "Lexington", "ROA": "Roanoke", "WAY": "Waynesboro"}
PY = "/usr/bin/python3"


def ledger(sentence):
    try:
        open(LEDGER, "a").write("| %s (native) | %s | %s | NEEDS_HUMAN: no | OPEN |\n"
                                % (dt.datetime.now(ET).strftime("%Y-%m-%d %H:%M ET"), AGENT, sentence))
    except OSError:
        pass


def pull(report, window, stores, tag):
    subprocess.run(["/bin/bash", os.path.join(HERE, "bravo_pull.sh"), report, window, ",".join(stores), "bonusclose-%s-%d" % (tag, int(time.time()))],
                   capture_output=True, text=True, timeout=7500)


def engine(stage, month):
    p = subprocess.run([PY, os.path.join(BONUS, "bin", "bonus_engine.py"), stage, "--month", month], capture_output=True, text=True, timeout=900, cwd=BONUS)
    return p.returncode, (p.stdout + p.stderr)[-2000:]


def fmt0(v):
    return "$" + format(round(v), ",")


def build_dm(month, nxt, notes):
    try:
        tg = json.load(open(os.path.join(BONUS, "data", nxt, "targets.json")))
    except (OSError, ValueError):
        tg = {}
    try:
        hist = json.load(open(os.path.join(BONUS, "data", "history.json"))).get(month, {})
    except (OSError, ValueError):
        hist = {}
    try:
        cur_t = json.load(open(os.path.join(BONUS, "data", month, "targets.json"))).get("targets", {})
    except (OSError, ValueError):
        cur_t = {}
    try:
        st = open(os.path.join(BONUS, "out", month, "slack_targets.txt")).read().strip()
    except OSError:
        st = ""
    mn, nn = dt.date(int(month[:4]), int(month[5:]), 1).strftime("%B"), dt.date(int(nxt[:4]), int(nxt[5:]), 1).strftime("%B")
    L = ["%s bonus targets (from the annual plan sheet%s):" % (nn, "" if tg.get("method") == "sheet" else " — NOT from the sheet this time, the trailing-12 fallback")]
    for s in STORES:
        L.append("• %s — %s" % (NAMES[s], fmt0(tg.get("targets", {}).get(s, 0)) if tg.get("targets", {}).get(s) else "no target on file"))
    L += ["", "%s results vs target:" % mn]
    for s in STORES:
        rev = (hist.get(s) or {}).get("net_revenue")
        t = cur_t.get(s)
        if rev is None:
            L.append("• %s — month-end numbers not in" % NAMES[s])
        elif t:
            L.append("• %s — %s vs %s target (%s)" % (NAMES[s], fmt0(rev), fmt0(t), ("hit, +" if rev >= t else "missed, -") + fmt0(abs(rev - t))[1:]))
        else:
            L.append("• %s — %s (no target was set)" % (NAMES[s], fmt0(rev)))
    if notes:
        L += [""] + notes
    if st:
        L += ["", "Ready to paste:", "```", st, "```"]
    L += ["", "Say the word and I'll post it to #bonus-goals — nothing has gone to the team."]
    return "\n".join(L)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    render, no_pull = "--render" in sys.argv, "--no-pull" in sys.argv
    now = dt.datetime.now(ET)
    if args:
        y, m = map(int, args[0].split("-"))
    else:
        d = now.date().replace(day=1) - dt.timedelta(days=1)
        y, m = d.year, d.month
    month = "%04d-%02d" % (y, m)
    nxt = "%04d-%02d" % ((y + 1, 1) if m == 12 else (y, m + 1))
    last = dt.date(y, m, calendar.monthrange(y, m)[1])
    window = "%s-01..%s" % (month, last)
    notes, log = [], []
    if not (render or no_pull):
        for rep in ("end-of-month", "chekkit-invites-range", "employee-activity-range"):
            pull(rep, window, STORES, rep[:6]); log.append("pulled " + rep)
        yf = glob.glob(os.path.join(BRAVO, "output", "%d_*_scrap-refining-gold.csv" % y))
        fresh = any(dt.datetime.fromtimestamp(os.path.getmtime(f)).date() == now.date() for f in yf)
        if fresh:
            log.append("gold: year files already refreshed today by the scrap rankings agent — no second pull")
        else:
            import scrap_rankings_monthly as srm
            bk = os.path.join(BRAVO, "output", "_backups_%s" % now.strftime("%Y%m%d")); os.makedirs(bk, exist_ok=True)
            for f in yf:
                shutil.copy2(f, bk)
            pm = dt.date(y, m, 1) - dt.timedelta(days=1)
            for s in STORES:
                pull("scrap-refining-gold", "%04d-%02d..%s" % (pm.year, pm.month, month), [s], "gold-" + s)
            log += srm.repair(apply=True) or ["gold: pulled %04d-%02d..%s per store, union-merged, nothing lost" % (pm.year, pm.month, month)]
    if not render:
        rc, out = engine("collect", month); log.append("collect rc=%d" % rc)
        if "hold" in out.lower() and not no_pull:
            miss = [s for s in STORES if s in out and "end-of-month" in out.lower()] or STORES
            pull("end-of-month", window, miss, "eom-retry"); rc, out = engine("collect", month); log.append("collect (retry) rc=%d" % rc)
        rc, out = engine("targets", month); log.append("targets rc=%d" % rc)
        if rc == 2:
            dm = "The %s bonus numbers are on hold — the month-end figures aren't all in yet. I'll follow up once they are." % dt.date(y, m, 1).strftime("%B")
            subprocess.run([PY, os.path.join(HERE, "vp_slack.py"), "dm", dm], capture_output=True, text=True, timeout=60, env=dict(os.environ, VP_TASK=AGENT))
            open(os.path.join(BONUS, "RUN_LOG.md"), "a").write("\n## %s — bonus-month-close-pull (native) HELD\n%s\n%s\n" % (now.strftime("%Y-%m-%d %H:%M"), "; ".join(log), out[-600:]))
            ledger("Bonus targets for %s held by the engine (exit 2); Joshua told in one line." % month)
            return 2
        p = subprocess.run([PY, os.path.join(BONUS, "bin", "sheet_sync.py"), "--month", month], capture_output=True, text=True, timeout=600, cwd=BONUS)
        log.append("sheet_sync rc=%d" % p.returncode)
        if p.returncode == 2:
            notes.append("The plan sheet couldn't be read this time, so these targets are the trailing-12 fallback — not the annual-plan numbers.")
        elif p.returncode != 0:
            notes.append("The plan sheet didn't update this time; targets above are the fallback numbers.")
            ledger("sheet_sync failed for %s (rc %d): %s" % (month, p.returncode, (p.stderr or p.stdout)[-200:].replace("\n", " ")))
    dm = build_dm(month, nxt, notes)
    if render:
        print("=== RENDER ONLY (no pull, no engine run) ===\n" + dm); return 0
    p = subprocess.run([PY, os.path.join(HERE, "vp_slack.py"), "dm", dm], capture_output=True, text=True, timeout=60, env=dict(os.environ, VP_TASK=AGENT))
    open(os.path.join(BONUS, "RUN_LOG.md"), "a").write("\n## %s — bonus-month-close-pull (native)\n%s; DM %s\n" % (now.strftime("%Y-%m-%d %H:%M"), "; ".join(log), "sent" if p.returncode == 0 else "FAILED"))
    if p.returncode != 0:
        ledger("Bonus targets draft for %s was built but the DM did not send." % month); return 1
    print("done", month)
    return 0


if __name__ == "__main__":
    sys.exit(main())
