#!/usr/bin/env python3
"""nics_monthly.py [YYYY-MM] [--render] [--no-pull] — native replacement for Cowork `nics-monthly-ranking`
(1st of month 09:30, 2026-10-02). The SKILL's steps, nothing re-derived:
  1 pull nics-transfers for the PRIOR full month, all 5 stores (bin/bravo_pull.sh), unless already on disk
  2 per store COUNT = data rows, REVENUE = sum of Amount (last field); rank by revenue (count tiebreak)
  3 post "FFL Transfers — <Month YYYY> (final)" to #ffl-transfer-performance: table Rank | Store | Revenue |
    Transfers + Total, one leader/laggard line, the trend-sheet link. A store with no file = "pending",
    and then the post says so (never presented as complete).
  4 refresh the Drive trend sheet: Bravo Data Extraction/ffl_trend_sync.py
The table is sent as a native Slack table (vp_slack converts markdown tables, as Claude's connector did).
"""
import calendar
import csv
import datetime as dt
import os
import re
import subprocess
import sys
from zoneinfo import ZoneInfo

AGENT = "nics-monthly-ranking"
ET = ZoneInfo("America/New_York")
OS_DIR = os.path.expanduser("~/Documents/Claude/Projects/Valley Pawn OS")
BIN = os.path.join(OS_DIR, "bin")
BRAVO = os.environ.get("VP_BRAVO_DIR") or os.path.expanduser("~/Documents/Claude/Projects/Bravo Data Extraction")
LEDGER = os.path.join(OS_DIR, "fleet", "FAILURE_LEDGER.md")
CH = "C0BPH5T1NFL"   # #ffl-transfer-performance
TREND = "https://docs.google.com/spreadsheets/d/1cek7S5KNKAywF_cPWgiASOZaNAVrF4e1EpMv-4KDURs/edit"
STORES = [("WAY", "Waynesboro"), ("CUL", "Culpeper"), ("HAR", "Harrisonburg"), ("LEX", "Lexington"), ("ROA", "Roanoke")]
PY = "/usr/bin/python3"


def money(s):
    s = (s or "").strip()
    neg = s.startswith("(") or s.startswith("-")
    v = float(re.sub(r"[^\d.]", "", s) or 0)
    return -v if neg else v


def usd(v):
    return "${:,.0f}".format(v) if float(v).is_integer() else "${:,.2f}".format(v)


def ledger(sentence):
    try:
        open(LEDGER, "a").write("| %s (native) | %s | %s | NEEDS_HUMAN: no | OPEN |\n"
                                % (dt.datetime.now(ET).strftime("%Y-%m-%d %H:%M ET"), AGENT, sentence))
    except OSError:
        pass


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    render, no_pull = "--render" in sys.argv, "--no-pull" in sys.argv
    if args:
        y, m = map(int, args[0].split("-"))
    else:
        first = dt.datetime.now(ET).date().replace(day=1) - dt.timedelta(days=1)
        y, m = first.year, first.month
    start = dt.date(y, m, 1)
    end = dt.date(y, m, calendar.monthrange(y, m)[1])
    path = lambda code: os.path.join(BRAVO, "output", "%s_to_%s_%s_nics-transfers.csv" % (start, end, code))
    missing = [c for c, _ in STORES if not os.path.exists(path(c))]
    if missing and not (render or no_pull):
        subprocess.run(["/bin/bash", os.path.join(BIN, "bravo_pull.sh"), "nics-transfers", "%s..%s" % (start, end),
                        ",".join(c for c, _ in STORES), "nics-month-%s-%d" % (start.strftime("%Y%m"), int(dt.datetime.now().timestamp()))],
                       capture_output=True, text=True, timeout=7500)
        missing = [c for c, _ in STORES if not os.path.exists(path(c))]
        if missing:   # SKILL: re-run any missing store ONCE
            subprocess.run(["/bin/bash", os.path.join(BIN, "bravo_pull.sh"), "nics-transfers", "%s..%s" % (start, end),
                            ",".join(missing), "nics-month-retry-%d" % int(dt.datetime.now().timestamp())],
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
    month = start.strftime("%B %Y")
    lines = ["*FFL Transfers — %s (final)*" % month if not pending else "*FFL Transfers — %s*" % month, "",
             "| Rank | Store | Revenue | Transfers |", "|---|---|---|---|"]
    for i, (name, rev, n) in enumerate(done, 1):
        lines.append("| %d | %s | %s | %d |" % (i, name, usd(rev), n))
    for name in pending:
        lines.append("| — | %s | pending | pending |" % name)
    lines.append("| | **Total** | **%s** | **%d** |" % (usd(sum(r[1] for r in done)), sum(r[2] for r in done)))
    lines.append("")
    if len(done) >= 2:
        lead, second, last = done[0], done[1], done[-1]
        gap = lead[1] - second[1]
        lines.append("%s led %s revenue at %s%s. %s trailed the field with %s across %d transfer%s." % (
            lead[0], start.strftime("%B"), usd(lead[1]),
            (", edging out %s by %s" % (second[0], usd(gap))) if gap > 0 else (", tied with %s" % second[0]),
            last[0], usd(last[1]), last[2], "" if last[2] == 1 else "s"))
    if pending:
        lines.append("%s %s still pending — this post will be completed when the data lands." % (", ".join(pending), "is" if len(pending) == 1 else "are"))
    lines += ["", "Trend sheet: [docs.google.com/spreadsheets/d/1cek7S5KNKAy…/edit](%s)" % TREND]
    post = "\n".join(lines)
    if render:
        print("=== RENDER ONLY ===\n" + post)
        return 0
    if pending:
        ledger("FFL transfer ranking for %s held — %s data missing after one retry." % (month, ", ".join(pending)))
        return 1
    tmp = "/tmp/nics_month_%s.txt" % start.strftime("%Y%m")
    open(tmp, "w").write(post)
    p = subprocess.run([PY, os.path.join(BIN, "vp_slack.py"), "post", CH, "--file", tmp],
                       capture_output=True, text=True, timeout=60, env=dict(os.environ, VP_TASK=AGENT))
    if p.returncode != 0:
        ledger("FFL transfer ranking for %s was built but did not post." % month)
        return 1
    subprocess.run([PY, os.path.join(BRAVO, "ffl_trend_sync.py")], capture_output=True, text=True, timeout=600)
    print("posted", month)
    return 0


if __name__ == "__main__":
    sys.exit(main())
