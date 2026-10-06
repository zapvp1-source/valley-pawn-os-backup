#!/usr/bin/env python3
"""items_to_price.py [--render] [--date YYYY-MM-DD] — native replacement for Cowork `daily-items-to-price`
(daily 08:00 ET, 2026-10-05). The SKILL's steps, nothing re-derived:
  1 FAST PATH: the native morning pull (com.valleypawn.morning-pull, 06:50) pulls items-to-price for TODAY
    and writes logs/_morning_pull_status_<DATE>.txt. Wait (up to ~75 min) for its `items-to-price` line.
    CLEAN + all 5 output/<DATE>_<STORE>_items-to-price.csv present -> compute + post.
  2 Otherwise RECOVERY (SKILL STEP 4.5): up to 2 rounds of bin/bravo_pull.sh items-to-price <DATE> <bad stores>,
    each store re-gated on the recovery pull's own log with the SAME integrity gate the morning pull uses
    (no "GAVE UP", and csv rows >= maxY-1 from the grid walker's seen=X/Y lines). Known case: Waynesboro's
    grid can stall at 241 of 247 rows ("Show More" unreachable) — that is TRUNCATED, never posted.
  3 COUNT = data rows, DOLLAR = sum of Cost. ALL-FIVE-OR-NOTHING: a missing/truncated store after recovery =
    post NOTHING, one ledger row + logs/_itp_incomplete_<DATE>.txt (as the SKILL says).
  4 Post to #items-to-price in the exact format of the past posts (italic markers, as Claude's connector
    rendered the SKILL's *...*). Self-dedupes on the title for the day.
--render: read what is on disk now, never pull, never post; prints the post and the gate verdict.
"""
import csv
import datetime as dt
import os
import re
import subprocess
import sys
import time
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

AGENT = "daily-items-to-price"
os.environ["VP_TASK"] = AGENT
ET = ZoneInfo("America/New_York")
OS_DIR = os.path.expanduser("~/Documents/Claude/Projects/Valley Pawn OS")
BIN = os.path.join(OS_DIR, "bin")
BRAVO = os.environ.get("VP_BRAVO_DIR") or os.path.expanduser("~/Documents/Claude/Projects/Bravo Data Extraction")
LEDGER = os.path.join(OS_DIR, "fleet", "FAILURE_LEDGER.md")
CH = "C0BA5U0GENL"   # #items-to-price
STORES = [("CUL", "Culpeper"), ("HAR", "Harrisonburg"), ("LEX", "Lexington"), ("ROA", "Roanoke"), ("WAY", "Waynesboro")]


def now():
    return dt.datetime.now(ET)


def ledger(sentence):
    try:
        open(LEDGER, "a").write("| %s (native) | %s | %s | NEEDS_HUMAN: no | OPEN |\n"
                                % (now().strftime("%Y-%m-%d %H:%M ET"), AGENT, sentence))
    except OSError:
        pass


def csv_path(date, code):
    return os.path.join(BRAVO, "output", "%s_%s_items-to-price.csv" % (date, code))


def tally(date, code):
    """(count, cost) exactly as the SKILL's STEP 4 script: DictReader rows, sum of Cost."""
    cnt, dsum = 0, 0.0
    with open(csv_path(date, code), newline="", encoding="utf-8-sig", errors="replace") as fh:
        for row in csv.DictReader(fh):
            cnt += 1
            v = (row.get("Cost") or "").replace("$", "").replace(",", "").strip()
            try:
                dsum += float(v)
            except ValueError:
                pass
    return cnt, dsum


def gate_store(date, code, log_id):
    """CLEAN / MISSING / TRUNCATED for one store against one pull log (same rule as morning_pull.sh)."""
    p = csv_path(date, code)
    if not os.path.exists(p):
        return "MISSING"
    try:
        log = open(os.path.join(BRAVO, "logs", log_id + ".log"), errors="replace").read()
    except OSError:
        log = ""
    sec = re.split(r"\n(?=\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} +Running items-to-price for )", log)
    mine = [x for x in sec if "Running items-to-price for %s" % code in x]
    txt = mine[-1] if mine else ""
    if "GAVE UP" in txt:
        return "TRUNCATED (gave up)"
    ys = [int(y) for _, y in re.findall(r"seen=(\d+)/(\d+)", txt)]
    maxy = max(ys) if ys else 0
    rows = sum(1 for _ in open(p, errors="replace")) - 1
    if maxy > 0 and rows < maxy - 1:
        return "TRUNCATED %d of %d" % (rows, maxy)
    return "CLEAN"


def certificate(date):
    """None (not written yet) / 'CLEAN' / 'FAILED X Y' from the morning-pull certificate."""
    try:
        for line in open(os.path.join(BRAVO, "logs", "_morning_pull_status_%s.txt" % date)):
            if line.startswith("items-to-price "):
                return line.split(" ", 1)[1].strip()
    except OSError:
        pass
    return None


def morning_log_id(date):
    logs = sorted(f for f in os.listdir(os.path.join(BRAVO, "logs"))
                  if f.startswith("morning-pull-%s" % date) and f.endswith(".log"))
    return logs[-1][:-4] if logs else ""


def build(date):
    d = dt.date.fromisoformat(date)
    lines = [":label: _Items to Price — %s_" % d.strftime("%b %d, %Y"),
             "Unpriced inventory awaiting pricing & floor placement, by store:", ""]
    tc, td = 0, 0.0
    for code, name in STORES:
        c, s = tally(date, code)
        tc += c
        td += s
        lines.append("• _%s (%s):_ %d items — %s" % (name, code, c, "${:,.2f}".format(s)))
    lines.append("_Total:_ %d items — %s" % (tc, "${:,.2f}".format(td)))
    return "\n".join(lines)


def main():
    render = "--render" in sys.argv
    date = now().date().isoformat()
    if "--date" in sys.argv:
        date = sys.argv[sys.argv.index("--date") + 1]
    title = "Items to Price — %s" % dt.date.fromisoformat(date).strftime("%b %d, %Y")

    # 1 — fast path: wait for the morning pull's certificate (it starts 06:50 and takes ~30-40 min)
    cert = certificate(date)
    if not render:
        t0 = time.time()
        while cert is None and time.time() - t0 < 75 * 60:
            time.sleep(60)
            cert = certificate(date)
    status = {}
    mlog = morning_log_id(date)
    for code, _ in STORES:
        if cert == "CLEAN" and os.path.exists(csv_path(date, code)):
            status[code] = "CLEAN"
        else:
            status[code] = gate_store(date, code, mlog) if mlog else ("MISSING" if not os.path.exists(csv_path(date, code)) else "UNVERIFIED")
            if cert and cert.startswith("FAILED") and code in cert.split()[1:] and status[code] == "CLEAN":
                status[code] = "FAILED in morning pull"
    print("certificate:", cert, "| gate:", status)

    # 2 — recovery, only for stores that are not clean (never in --render)
    rnd = 0
    while not render and any(v != "CLEAN" for v in status.values()) and rnd < 2:
        rnd += 1
        bad = [c for c, v in status.items() if v != "CLEAN"]
        rid = "itp-recover-%s-r%d-%d" % (date, rnd, int(time.time()))
        print("recovery round %d for %s (%s)" % (rnd, ",".join(bad), rid))
        subprocess.run(["/bin/bash", os.path.join(BIN, "bravo_pull.sh"), "items-to-price", date, ",".join(bad), rid],
                       capture_output=True, text=True, timeout=7500)
        for c in bad:
            status[c] = gate_store(date, c, rid)
        print("after round %d:" % rnd, status)

    bad = {c: v for c, v in status.items() if v != "CLEAN"}
    if bad:
        detail = ", ".join("%s %s" % (dict(STORES)[c], v.lower()) for c, v in bad.items())
        if render:
            print("=== HOLD (render) — would post nothing: %s ===" % detail)
            return 2
        try:
            clean = " ".join("%s=%d" % (c, tally(date, c)[0]) for c in status if status[c] == "CLEAN")
            open(os.path.join(BRAVO, "logs", "_itp_incomplete_%s.txt" % date), "a").write(
                "%s INCOMPLETE: %s | clean: %s\n" % (now().isoformat(), " ".join("%s=%s" % kv for kv in bad.items()), clean))
        except OSError:
            pass
        ledger("Items-to-price report for %s not posted — %s after recovery." % (date, detail))
        return 1

    post = build(date)
    if render:
        print("=== RENDER ONLY ===\n" + post)
        return 0
    import vp_slack
    if vp_slack.has(CH, title, 20):
        print("already posted:", title)
        return 0
    tmp = "/tmp/items_to_price_%s.txt" % date
    open(tmp, "w").write(post)
    p = subprocess.run(["/usr/bin/python3", os.path.join(BIN, "vp_slack.py"), "post", CH, "--file", tmp],
                       capture_output=True, text=True, timeout=60, env=dict(os.environ, VP_TASK=AGENT))
    if p.returncode != 0:
        ledger("Items-to-price report for %s was built but did not post (%s)." % (date, (p.stderr or "").strip()[:150]))
        return 1
    print("posted", title)
    return 0


if __name__ == "__main__":
    sys.exit(main())
