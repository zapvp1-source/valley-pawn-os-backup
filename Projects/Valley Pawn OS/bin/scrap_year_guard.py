#!/usr/bin/env python3
"""scrap_year_guard.py [--render] [--seed] — a scrap YEAR file can never shrink again (2026-10-20).

WHY: every `scrap-refining-gold` pull REWRITES output/<YYYY>_<STORE>_scrap-refining-gold.csv with only the rows its
window captured. On 10/15 11:47–12:00 a narrow re-pull (trigger goldverify-20261015-1547, the interactive bonus
gold re-check — NOT scrap-bucket-name-check, which is a list-only inventory through the scrap watcher and writes
only results-scrap/*.buckets.csv) truncated CUL 20 -> 17 rows, WAY 22 -> 20 and swapped HAR's Aug/Sep buckets for
"NO BUCKET FOUND" fillers. Any caller can do that (a scheduled agent, a Cowork task, an interactive session), so the
guard sits on the FILES, not on one caller.

HOW (additive only, stdlib):
  * a high-water copy of every year file lives in output/_scrap_year_guard/<name> = the last good version (current rows
    plus any restored ones).
  * each run (launchd every 10 min + RunAtLoad): for each year file not modified in the last 90 s (a pull may be
    mid-write), if a PHYSICAL bucket (Store + CreatedOn; see phys()) in its high-water copy is missing from it, the current file is copied to
    output/_scrap_year_guard/shrunk/<name>.<YYYYMMDD-HHMMSS> and rewritten as the union; one FAILURE_LEDGER row
    (NEEDS_HUMAN: no) and a log line say so. Otherwise the high-water copy just absorbs any new rows.
  * --seed (first run, also automatic when a high-water copy is missing): the union also takes in the two newest
    output/_backups_* sets and the file's own .bak-* siblings written since 2026-09-01 — that is what puts back the
    rows the 10/15 truncation removed. `.corrupted-*` copies are never read.
  * --render: prints what it would do, writes nothing.
Never touches Bravo, never posts, never deletes a row.
"""
import csv
import datetime as dt
import glob
import os
import re
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
OS_DIR = os.path.dirname(HERE)
OUT = os.path.join(os.path.dirname(OS_DIR), "Bravo Data Extraction", "output")
GUARD = os.path.join(OUT, "_scrap_year_guard")
SHRUNK = os.path.join(GUARD, "shrunk")
LEDGER = os.path.join(OS_DIR, "fleet", "FAILURE_LEDGER.md")
LOG = os.path.expanduser("~/Library/Logs/valleypawn/scrap-year-guard.log")
NAME = re.compile(r"^20\d\d_[A-Z]{3}_scrap-refining-gold\.csv$")


def log(line, render):
    s = "%s %s%s" % (dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "RENDER " if render else "", line)
    print(s)
    if not render:
        os.makedirs(os.path.dirname(LOG), exist_ok=True)
        open(LOG, "a").write(s + "\n")


def read(p):
    """(header, rows) exactly as stored."""
    try:
        with open(p, newline="", encoding="utf-8-sig") as fh:
            rows = [r for r in csv.reader(fh) if r]
    except OSError:
        return None, []
    if rows and rows[0] and rows[0][0] == "Store":
        return rows[0], rows[1:]
    return None, rows


def key(r):
    return tuple(x.strip() for x in r)


def phys(r):
    """The physical bucket a row describes: (Store, CreatedOn) on the 7-column files — CreatedOn is the stable
    per-bucket timestamp scrap_rankings.load_raw keys on, and it survives a RENAME (scrap-bucket-name-check asks
    managers to rename) — or (Store, Month, BucketName) on the 4-column 2025 files. A 'NO BUCKET FOUND' filler row
    has no physical bucket (None): it is never restored and never blocks a restore."""
    if len(r) < 3 or r[2].strip() in ("", "NO BUCKET FOUND"):
        return None
    if len(r) >= 7 and r[3].strip():
        return (r[0].strip(), r[3].strip())
    return (r[0].strip(), r[1].strip(), r[2].strip())


def union(*lists):
    seen, out = set(), []
    for rows in lists:
        for r in rows:
            k = key(r)
            if k not in seen and r and r[0] != "Store":
                seen.add(k); out.append(r)
    return out


def key_set(rows):
    return {key(r) for r in rows}


def write(p, hdr, rows):
    tmp = p + ".guardtmp"
    with open(tmp, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        if hdr:
            w.writerow(hdr)
        w.writerows(rows)
    os.replace(tmp, p)


def seed_sources(name):
    srcs = []
    for d in sorted(glob.glob(os.path.join(OUT, "_backups_2*")))[-2:]:
        srcs.append(os.path.join(d, name))
    for b in glob.glob(os.path.join(OUT, name + ".bak-*")):
        m = re.search(r"\.bak-(\d{8})", b)
        if m and m.group(1) >= "20260901":
            srcs.append(b)
    return [s for s in srcs if os.path.exists(s)]


def main():
    render = "--render" in sys.argv
    force_seed = "--seed" in sys.argv
    if not render:
        os.makedirs(SHRUNK, exist_ok=True)
    events = []
    for p in sorted(glob.glob(os.path.join(OUT, "20*_*_scrap-refining-gold.csv"))):
        name = os.path.basename(p)
        if not NAME.match(name):
            continue
        if time.time() - os.path.getmtime(p) < 90:
            log("%s modified < 90 s ago — skipped this pass (a pull may be writing it)" % name, render)
            continue
        hdr, cur = read(p)
        hw_path = os.path.join(GUARD, name)
        _, hw = read(hw_path)
        extra = []
        if force_seed or not os.path.exists(hw_path):
            for s in seed_sources(name):
                extra.append(read(s)[1])
        seen_all = union(hw, *extra)
        cur_phys = {phys(r) for r in cur} - {None}
        cur_names = {(r[0].strip(), r[2].strip()) for r in cur if len(r) >= 3}
        # restore only rows whose PHYSICAL bucket is absent from the file now (a newer read of the same bucket — a
        # rename, an OPEN->CLOSED change, a re-read weight — supersedes the older row and is never doubled)
        lost, lost_phys = [], set()
        for r in seen_all:
            k = phys(r)
            if len(r) >= 7 and not r[3].strip() and (r[0].strip(), r[2].strip()) in cur_names:
                continue   # an older read with no CreatedOn of a bucket the file still holds (by name) — never doubled
            if k is not None and k not in cur_phys:
                lost.append(r); lost_phys.add(k)
        full = union(cur, lost)
        if lost:
            stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
            merged = full
            log("%s: %d rows on disk lack %d row(s) the guard has seen -> restored to %d rows (copy of the shrunk file: "
                "_scrap_year_guard/shrunk/%s.%s)" % (name, len(cur), len(lost), len(merged), name, stamp), render)
            for r in lost[:12]:
                log("   restored row: %s" % ",".join(r), render)
            if not render:
                shutil.copy2(p, os.path.join(SHRUNK, "%s.%s" % (name, stamp)))
                write(p, hdr or ["Store", "Month", "BucketName", "CreatedOn", "Status", "StatusDate", "CombinedMetalWeightDwt"], merged)
                write(hw_path, hdr, merged)
            events.append("%s (+%d rows)" % (name, len(lost)))
        else:
            if not render and (key_set(full) != key_set(hw) or not os.path.exists(hw_path)):
                write(hw_path, hdr, full)
            log("%s: ok (%d rows on disk, high-water %d)" % (name, len(cur), len(full)), render) if render else None
    if events and not render:
        try:
            open(LEDGER, "a").write("| %s (native) | scrap-year-guard | a scrap pull shrank %s; the missing rows were put "
                                    "back automatically and the shrunk copy kept | NEEDS_HUMAN: no | OPEN |\n"
                                    % (dt.datetime.now().strftime("%Y-%m-%d %H:%M ET"), ", ".join(events)))
        except OSError:
            pass
    if render:
        print("RENDER summary: %s" % (", ".join(events) or "nothing to restore"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
