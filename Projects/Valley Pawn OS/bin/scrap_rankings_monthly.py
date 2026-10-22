#!/usr/bin/env python3
"""scrap_rankings_monthly.py [YYYY-MM] [--render] [--no-pull] — native `monthly-scrap-rankings`
(1st of month 04:30 ET; Mac-first wave 3, 2026-10-19). The SKILL's steps, in order, nothing re-derived:
  2a back up every output/202*_*_scrap-refining-gold.csv to output/_backups_<YYYYMMDD>/ (a pull TRUNCATES the year file)
  2b pull window P-1..P (P = the month just ended = the POSTED month), ONE store per trigger, through
     bin/bravo_pull.sh; a store whose pull errors is re-dropped once (navigation failures are the norm)
  2c merge the pull back onto the backup additively (Bravo Data Extraction/_merge_scrap_weights.py, same code,
     pointed at today's backup folder) and confirm no store lost rows
  3  scrap_rankings.py build + report P (its slack_post() IS the post)
  4  quality gate: no reported-month bucket missing a weight or LOW-CONF; zero blank-weight buckets Jan..P in
     either year; a store with nothing posted is named plainly (the 2026-10-01 live line) only when its pull
     succeeded — a store whose pull failed is a gap, and the board is held
  5  scrap_trend_sheet.py -> Valley Pawn Drive/Trends workbook (Drive for Desktop path, native)
  6  post to #scrap-rankings (C05EHBH4G67) as the ops bot, dedupe on the lead line (30 d)
  7  log to Bravo Data Extraction/SCRAP_RANKINGS_STATUS.md
--render: steps 3-4 on the files already on disk, prints the post, writes nothing, pulls nothing.
Never runs inside 18:00–19:15 ET (Bravo evening window) — the 04:30 slot is deliberate (SKILL scheduling note).
"""
import calendar
import csv
import datetime as dt
import glob
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import time
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
AGENT = "monthly-scrap-rankings"
ET = ZoneInfo("America/New_York")
OS_DIR = os.path.dirname(HERE)
BRAVO = os.path.expanduser("~/Documents/Claude/Projects/Bravo Data Extraction")
OUT = os.path.join(BRAVO, "output")
LEDGER = os.path.join(OS_DIR, "fleet", "FAILURE_LEDGER.md")
STATUS = os.path.join(BRAVO, "SCRAP_RANKINGS_STATUS.md")
CH = "C05EHBH4G67"
STORES = ["CUL", "HAR", "LEX", "ROA", "WAY"]
NAMES = {"CUL": "Culpeper", "HAR": "Harrisonburg", "LEX": "Lexington", "ROA": "Roanoke", "WAY": "Waynesboro"}
PY = "/usr/bin/python3"


def ledger(sentence):
    try:
        open(LEDGER, "a").write("| %s (native) | %s | %s | NEEDS_HUMAN: no | OPEN |\n"
                                % (dt.datetime.now(ET).strftime("%Y-%m-%d %H:%M ET"), AGENT, sentence))
    except OSError:
        pass


def load_mod(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def row_count(p):
    try:
        with open(p, newline="", encoding="utf-8-sig") as fh:
            return sum(1 for r in csv.reader(fh) if r and r[0] != "Store")
    except OSError:
        return 0


def pull_store(store, window, tag):
    tid = "scrap-monthly-%s-%s-%s" % (tag, int(time.time()), store)
    subprocess.run(["/bin/bash", os.path.join(HERE, "bravo_pull.sh"), "scrap-refining-gold", window, store, tid],
                   capture_output=True, text=True, timeout=3000)
    rp = os.path.join(BRAVO, "results", tid + ".result.json")
    try:
        r = json.load(open(rp))
        txt = json.dumps(r).lower()
        ok = '"status": "success"' in txt or '"status":"success"' in txt or ('"success"' in txt and '"error"' not in txt)
        return ok, tid
    except (OSError, ValueError):
        return False, tid


HDR = ["Store", "Month", "BucketName", "CreatedOn", "Status", "StatusDate", "CombinedMetalWeightDwt"]


def read_rows(p):
    """Rows exactly as stored (the 2025 files are 4-column, the 2026 files 7-column — never reshape them)."""
    try:
        with open(p, newline="", encoding="utf-8-sig") as fh:
            return [r for r in csv.reader(fh) if r and r[0] != "Store"]
    except OSError:
        return []


def union_rows(copies):
    """Additive union: every DISTINCT row from the copy on disk and every backup copy, in that order. Nothing is
    collapsed here — scrap_rankings.load_raw already dedupes the same bucket across query windows and lets a CLOSED
    read beat a stale OPEN one — so a row is never dropped and a weight can never be blanked."""
    seen, out = set(), []
    for rows in copies:
        for r in rows:
            k = tuple(x.strip() for x in r)
            if k not in seen:
                seen.add(k); out.append(r)
    return out


def repair(apply, dest=None):
    """2026-10-19 finding: the 10/15 scrap-bucket-name-check full-year pull TRUNCATED the 2026 year files with no
    backup/merge of its own (CUL 20->17 rows, WAY 22->20, HAR lost its Aug/Sep buckets behind 'NO BUCKET FOUND'
    fillers at the same row count). Before pulling, rebuild every year file as the additive union of the copy on
    disk and EVERY backup copy under output/_backups_*, so a truncation elsewhere never silently shrinks the
    history this board is built from. apply=False writes the repaired copies to `dest` instead (render)."""
    notes = []
    baks = sorted(glob.glob(os.path.join(OUT, "_backups_2*")))[-2:]   # the two newest backup sets (older ones predate fixes)
    names = sorted({os.path.basename(f) for f in glob.glob(os.path.join(OUT, "202*_*_scrap-refining-gold.csv"))
                    + [g for d in baks for g in glob.glob(os.path.join(d, "202*_*_scrap-refining-gold.csv"))]})
    for b in names:
        cur = os.path.join(OUT, b)
        copies = [read_rows(cur)] + [read_rows(os.path.join(d, b)) for d in reversed(baks)]
        u = union_rows(copies)
        before = read_rows(cur)
        if len(u) == len(before) and all(x == y for x, y in zip(u, before)):
            if dest:
                shutil.copy2(cur, dest) if os.path.exists(cur) else None
            continue
        notes.append("%s: %d rows on disk -> %d after union with backups%s" % (b, len(before), len(u), "" if apply else " (render copy only)"))
        target = cur if apply else os.path.join(dest, b)
        hdr = HDR if any(len(r) >= 7 for r in u) else HDR[:3] + HDR[-1:]
        with open(target, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh); w.writerow(hdr); w.writerows(u)
    return notes


def read_history(p):
    try:
        return list(csv.DictReader(open(p, newline="")))
    except OSError:
        return []


def keep_posted(history, prev_rows):
    """SKILL: 'a posted bucket never changes after the fact'. A weighted bucket that was in the previous history
    but is absent from the rebuilt one (a year file lost it — the 10/15 truncation) is carried forward, so a
    board already in front of the stores can never silently shrink. Additive only; nothing is overwritten."""
    cur = read_history(history)
    have = {(r["store"], r["period"], r["bucket"]) for r in cur}
    carried = [r for r in prev_rows if r.get("dwt") and (r["store"], r["period"], r["bucket"]) not in have]
    if not carried:
        return []
    with open(history, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["store", "period", "year", "month", "bucket", "dwt", "date_source"])
        w.writeheader()
        for r in sorted(cur + carried, key=lambda x: (x["store"], x["period"], x["bucket"])):
            w.writerow({k: r.get(k, "") for k in w.fieldnames})
    return ["carried forward %d posted bucket(s) missing from the raw files: %s" % (len(carried), ", ".join("%s %s %s" % (r["store"], r["period"], r["bucket"]) for r in carried[:8]))]


def gate(history, period, ok_stores):
    """SKILL step 4. -> (problems[], zero_stores[])"""
    y = int(period[:4]); mm = int(period[5:7])
    rows = [r for r in csv.DictReader(open(history))]
    probs = []
    cur = [r for r in rows if r["period"] == period]
    miss = [r for r in cur if not r["dwt"]]
    low = [r for r in cur if r["date_source"].startswith("LOW-CONF")]
    if miss:
        probs.append("missing weight in %s: %s" % (period, ", ".join("%s %s" % (r["store"], r["bucket"]) for r in miss)))
    if low:
        probs.append("LOW-CONF date in %s: %s" % (period, ", ".join("%s %s" % (r["store"], r["bucket"]) for r in low)))
    ytd = [r for r in rows if not r["dwt"] and int(r["period"][5:7]) <= mm and r["period"][:4] in (str(y), str(y - 1))]
    if ytd:
        probs.append("blank-weight buckets in the YTD span: %s" % ", ".join("%s %s %s" % (r["store"], r["period"], r["bucket"]) for r in ytd[:10]))
    stores_with = {r["store"] for r in cur}
    zero = [s for s in STORES if s not in stores_with]
    gaps = [s for s in zero if s not in ok_stores]
    if gaps:
        probs.append("no %s bucket and the pull did not succeed for %s" % (period, ", ".join(gaps)))
    return probs, zero


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    render, no_pull = "--render" in sys.argv, "--no-pull" in sys.argv
    now = dt.datetime.now(ET)
    if args:
        y, m = map(int, args[0].split("-"))
    else:
        d = now.date().replace(day=1) - dt.timedelta(days=1)
        y, m = d.year, d.month
    period = "%04d-%02d" % (y, m)
    pm = dt.date(y, m, 1) - dt.timedelta(days=1)
    window = "%04d-%02d..%s" % (pm.year, pm.month, period)
    sr = load_mod("scrap_rankings", os.path.join(BRAVO, "scrap_rankings.py"))
    ok_stores, notes = set(STORES) if (render or no_pull) else set(), []
    if render:   # never touch production files from a render: repaired copies + history go to fleet/test_output
        rd = os.path.join(OS_DIR, "fleet", "test_output", "scrap_render_%s_%s" % (period, now.strftime("%H%M%S")))
        os.makedirs(rd, exist_ok=True)
        notes += repair(apply=False, dest=rd)
        for f in glob.glob(os.path.join(OUT, "*scrap-refining-gold*.csv")):   # diagnostics etc. that repair skips
            if not os.path.exists(os.path.join(rd, os.path.basename(f))):
                shutil.copy2(f, rd)
        sr.OUT, sr.HISTORY = rd, os.path.join(rd, "scrap_history.csv")
    else:
        notes += repair(apply=True)
    if not (render or no_pull):
        if dt.time(18, 0) <= now.time() <= dt.time(19, 15):
            ledger("Scrap rankings pull skipped — started inside the evening Bravo window."); return 2
        bk = os.path.join(OUT, "_backups_%s" % now.strftime("%Y%m%d"))
        os.makedirs(bk, exist_ok=True)
        files = glob.glob(os.path.join(OUT, "202*_*_scrap-refining-gold.csv"))
        for f in files:
            shutil.copy2(f, bk)
        before = {os.path.basename(f): row_count(f) for f in files}
        notes.append("backup %s (%d files)" % (os.path.basename(bk), len(files)))
        for s in STORES:
            ok, tid = pull_store(s, window, "a")
            if not ok:
                ok, tid = pull_store(s, window, "b")
            notes.append("%s pull %s (%s)" % (s, "ok" if ok else "FAILED twice", tid))
            if ok:
                ok_stores.add(s)
        mg = load_mod("merge_scrap", os.path.join(BRAVO, "_merge_scrap_weights.py"))
        mg.BAK = bk
        for s in STORES:
            for yr in sorted({os.path.basename(f)[:4] for f in files}):
                mg.merge(s, yr)
        lost = [n for n, c in before.items() if row_count(os.path.join(OUT, n)) < c]
        if lost:
            ledger("Scrap rankings held — a pull left %s shorter than its backup after the merge." % ", ".join(lost)); return 2
    prev_hist = read_history(sr.HISTORY if not render else os.path.join(OUT, "scrap_history.csv"))
    sr.build()
    notes += keep_posted(sr.HISTORY, prev_hist)
    r = sr.report(period)
    probs, zero = gate(sr.HISTORY, period, ok_stores)
    post = sr.slack_post(r)
    if zero and not probs:
        names = [NAMES[s] for s in zero]
        txt = (" and ".join(names) if len(names) <= 2 else ", ".join(names[:-1]) + " and " + names[-1])
        line = "%s %s closed out a gold batch as of today, so %s not on this month's board — %s show up once %s batch closes." % (
            txt, "hadn't" if len(names) > 1 else "hadn't", "they're" if len(names) > 1 else "it's", "they'll" if len(names) > 1 else "it'll", "their" if len(names) > 1 else "its")
        parts = post.split("\n\n")
        parts.insert(2, line) if len(parts) > 2 else parts.append(line)
        post = "\n\n".join(parts)
    if render:
        print("=== RENDER ONLY (%s, window %s) ===\n%s\n\n=== GATE ===\n%s\n=== REPAIR NOTES ===\n%s" % (period, window, post, "\n".join(probs) or "PASS", "\n".join(notes) or "none"))
        return 0 if not probs else 2
    stamp = now.strftime("%Y-%m-%d %H:%M ET")
    if probs:
        ledger("Scrap rankings for %s held — %s." % (period, "; ".join(probs)[:300]))
        open(STATUS, "a").write("\n## %s — HELD (%s, native)\n\n- %s\n- pulls: %s\n" % (stamp, period, "\n- ".join(probs), "; ".join(notes)))
        print("HOLD — " + "; ".join(probs)); return 2
    subprocess.run([PY, os.path.join(BRAVO, "scrap_trend_sheet.py")], capture_output=True, text=True, timeout=600, cwd=BRAVO)
    import vp_slack
    os.environ["VP_TASK"] = AGENT
    lead = post.splitlines()[0]
    if vp_slack.has(CH, lead[:60], 24 * 30):
        print("already posted for", period); return 0
    tmp = "/tmp/scrap_rankings_%s.txt" % period
    open(tmp, "w").write(post)
    p = subprocess.run([PY, os.path.join(HERE, "vp_slack.py"), "post", CH, "--file", tmp], capture_output=True, text=True,
                       timeout=60, env=dict(os.environ, VP_TASK=AGENT))
    if p.returncode != 0:
        ledger("Scrap rankings for %s were built but did not post." % period)
        print("post failed:", p.stderr.strip()[:200]); return 1
    if "DRY RUN" in p.stdout:   # publish guard diverted the post: never record it as POSTED
        print(p.stdout.strip()); return 0
    open(STATUS, "a").write("\n## %s — POSTED (%s, native agent)\n\n- Window %s, one trigger per store: %s\n- Company %s dwt; stores with nothing posted: %s\n- Trend workbook rewritten (scrap_trend_sheet.py)\n- Slack ts %s\n"
                            % (stamp, period, window, "; ".join(notes) or "no pull (files on disk)", format(r["total"], ",.0f"), ", ".join(NAMES[s] for s in zero) or "none", p.stdout.strip()))
    print("posted", period)
    return 0


if __name__ == "__main__":
    sys.exit(main())
