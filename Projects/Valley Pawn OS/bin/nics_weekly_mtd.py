#!/usr/bin/env python3
"""nics_weekly_mtd.py [--render] — native replacement for Cowork `nics-weekly-mtd-ranking`.
Weekly MONTH-TO-DATE FFL transfer ranking, ranked by revenue, posted to #ffl-transfer-performance.
Distinct from nics_monthly.py (which posts the PRIOR month's FINAL number on the 1st) — this one
posts the CURRENT month's in-progress number, any day it's run, and is always labeled "Month-to-Date"
so it's never mistaken for a final figure. Added 2026-10-05 per the DATA-FIRST GATE OVERRIDE in the
nics-weekly-mtd-ranking SKILL: the old osascript/Control_your_Mac path doesn't exist anymore, so this
is a proper native host_queue-callable script instead of a Cowork session trying to drive Bravo itself.

  1 pull nics-transfers for month-to-date (1st of this month .. today), all 5 stores (bin/bravo_pull.sh),
    reusing any CSV already on disk for that exact range.
  2 per store COUNT = data rows, REVENUE = sum of Amount (last field); rank by revenue (count tiebreak).
  3 post "FFL Transfers — Month-to-Date (<Month> 1-<day>)" to #ffl-transfer-performance: table
    Rank | Store | Revenue | Transfers + Total, one leader/laggard line. A store with no file after one
    retry = withheld: NOTHING is posted, one ledger row (all-five-or-nothing, as nics_monthly.py; changed
    2026-10-05 — previously posted with "pending" rows). --render still shows the would-be table.
"""
import calendar
import csv
import datetime as dt
import os
import re
import subprocess
import sys
from zoneinfo import ZoneInfo

AGENT = "nics-weekly-mtd-ranking"
ET = ZoneInfo("America/New_York")
OS_DIR = os.path.expanduser("~/Documents/Claude/Projects/Valley Pawn OS")
BIN = os.path.join(OS_DIR, "bin")
BRAVO = os.environ.get("VP_BRAVO_DIR") or os.path.expanduser("~/Documents/Claude/Projects/Bravo Data Extraction")
LEDGER = os.path.join(OS_DIR, "fleet", "FAILURE_LEDGER.md")
CH = "C0BPH5T1NFL"   # #ffl-transfer-performance
STORES = [("WAY", "Waynesboro"), ("CUL", "Culpeper"), ("HAR", "Harrisonburg"), ("LEX", "Lexington"), ("ROA", "Roanoke")]
PY = "/usr/bin/python3"


def money(s):
    s = (s or "").strip()
    neg = s.startswith("(") or s.startswith("-")
    v = float(re.sub(r"[^\d.]", "", s) or 0)
    return -v if neg else v


def usd(v):
    return "${:,.0f}".format(v) if float(v).is_integer() else "${:,.2f}".format(v)


def ledger(sentence, needs_human="no"):
    try:
        open(LEDGER, "a").write("| %s (native) | %s | %s | NEEDS_HUMAN: %s | OPEN |\n"
                                % (dt.datetime.now(ET).strftime("%Y-%m-%d %H:%M ET"), AGENT, sentence, needs_human))
    except OSError:
        pass


def main():
    render = "--render" in sys.argv
    today = dt.datetime.now(ET).date()
    if "--end" in sys.argv:   # render/backfill a past MTD window, e.g. --end 2026-09-28
        today = dt.date.fromisoformat(sys.argv[sys.argv.index("--end") + 1])
    start = today.replace(day=1)
    end = today
    path = lambda code: os.path.join(BRAVO, "output", "%s_to_%s_%s_nics-transfers.csv" % (start, end, code))
    missing = [c for c, _ in STORES if not os.path.exists(path(c))]
    if missing and not render:
        p = subprocess.run(["/bin/bash", os.path.join(BIN, "bravo_pull.sh"), "nics-transfers", "%s..%s" % (start, end),
                            ",".join(c for c, _ in STORES), "nics-mtd-%s-%d" % (start.strftime("%Y%m%d"), int(dt.datetime.now().timestamp()))],
                           capture_output=True, text=True, timeout=7500)
        missing = [c for c, _ in STORES if not os.path.exists(path(c))]
        if missing:   # re-run any missing store ONCE, single-store trigger
            subprocess.run(["/bin/bash", os.path.join(BIN, "bravo_pull.sh"), "nics-transfers", "%s..%s" % (start, end),
                            ",".join(missing), "nics-mtd-retry-%d" % int(dt.datetime.now().timestamp())],
                           capture_output=True, text=True, timeout=7500)
            missing = [c for c, _ in STORES if not os.path.exists(path(c))]
    rows = []
    for code, name in STORES:
        if code in missing:
            rows.append((name, None, None))
            continue
        with open(path(code), newline="", errors="replace") as fh:
            data = [r for r in csv.reader(fh)][1:]
        data = [r for r in data if r and any(c.strip() for c in r)]
        rows.append((name, sum(money(r[-1]) for r in data), len(data)))
    done = sorted([r for r in rows if r[1] is not None], key=lambda r: (-r[1], -r[2]))
    pending = [r[0] for r in rows if r[1] is None]

    if not done:
        ledger("Weekly MTD FFL ranking for %s produced no data — all 5 stores missing after one retry." % start.strftime("%B %Y"))
        return 1

    title = "FFL Transfers — Month-to-Date (%s 1–%d)" % (start.strftime("%B"), end.day)   # en dash, as the 9/21 + 9/29 posts
    lines = ["*%s*" % title, "", "| Rank | Store | Revenue | Transfers |", "|---|---|---|---|"]
    for i, (name, rev, n) in enumerate(done, 1):
        lines.append("| %d | %s | %s | %d |" % (i, name, usd(rev), n))
    for name in pending:
        lines.append("| — | %s | pending | pending |" % name)
    lines.append("| | **Total** | **%s** | **%d** |" % (usd(sum(r[1] for r in done)), sum(r[2] for r in done)))
    lines.append("")
    if len(done) >= 2:
        lead, second, last = done[0], done[1], done[-1]
        gap = lead[1] - second[1]
        lines.append("%s leads month-to-date revenue at %s%s. %s trails the field with %s across %d transfer%s." % (
            lead[0], usd(lead[1]),
            (", edging out %s by %s" % (second[0], usd(gap))) if gap > 0 else (", tied with %s" % second[0]),
            last[0], usd(last[1]), last[2], "" if last[2] == 1 else "s"))
    elif len(done) == 1:
        lines.append("%s is the only store with data so far this run." % done[0][0])
    if pending:
        lines.append("%s %s pending — this figure is incomplete until %s land%s." % (
            ", ".join(pending), "is" if len(pending) == 1 else "are",
            ", ".join(pending), "s" if len(pending) == 1 else ""))
    post = "\n".join(lines)

    if render:
        print("=== RENDER ONLY ===\n" + post)
        if pending:
            print("=== HOLD — a live run would post NOTHING (all 5 stores required); ledger row instead ===")
        return 0
    # 2026-10-05 (native conversion): all-five-or-nothing, matching nics_monthly.py. The 10/5 10:07 post went out
    # with 3 stores "pending"; a store Bravo can't render is withheld, not shown as pending.
    if pending:
        ledger("Weekly MTD FFL ranking for %s held — %s data missing after one retry." % (start.strftime("%B %Y"), ", ".join(pending)))
        return 1
    sys.path.insert(0, BIN)
    import vp_slack
    if vp_slack.has(CH, title, 20):
        print("already posted:", title)
        return 0

    tmp = "/tmp/nics_weekly_mtd_%s.txt" % today.isoformat()
    open(tmp, "w").write(post)
    p = subprocess.run([PY, os.path.join(BIN, "vp_slack.py"), "post", CH, "--file", tmp],
                       capture_output=True, text=True, timeout=60, env=dict(os.environ, VP_TASK=AGENT))
    if p.returncode != 0:
        ledger("Weekly MTD FFL ranking for %s was built but did not post (%s)." % (start.strftime("%B %Y"), (p.stderr or "").strip()[:200]))
        return 1
    print("posted MTD", start, "..", end)
    return 0


if __name__ == "__main__":
    sys.exit(main())
