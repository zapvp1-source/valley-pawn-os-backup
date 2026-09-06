#!/usr/bin/env python3
"""
monthly_prestage_runner.py — native (no-Claude) pre-stage of the 6 End-of-Month
date-window XLSX files that `monthly-analytics-report` consumes on the 1st.

WHY THIS EXISTS (2026-09-05): the Cowork task `monthly-analytics-prestage` was a
Claude (haiku) session doing a ~60-minute serial drop → poll → copy loop. Twice in
a row (July, August 2026) the session ended after queuing the triggers and never
performed the copy step, so the six windows that share an end date overwrote each
other on disk and the monthly company report could not post. This script owns the
loop instead; it runs under launchd and needs no Claude session at all.

Behaviour
- Gate: runs only when tomorrow is the 1st (unless --force / --report-month given).
- For each of the 6 windows, IN ORDER: drop one trigger, wait for its result.json,
  copy every successful cell's output file (path taken from result.json — never
  guessed from the date) to the window-tagged sidecar, then move to the next window.
- Idempotent / resumable: a window whose 5 sidecar files already exist (>2 KB) is
  skipped, so a re-run only fills gaps.
- One focused retry per window for the stores that failed.
- Writes the same `{YYYY-MM} Prestage.md` working file the old task wrote, plus a
  plain log under Valley Pawn OS/monthly-analytics/logs/.
- Silent: no Slack, no DM. The 7 AM `monthly-analytics-watchdog` remains the
  notification path.

Additive-only: does not touch EndOfMonth.ahk, bravo_watcher.ahk, or any other task.
"""
import argparse
import calendar
import datetime as dt
import json
import os
import shutil
import sys
import time

HOME = os.path.expanduser("~")
BDE = os.path.join(HOME, "Documents/Claude/Projects/Bravo Data Extraction")
TRIGGERS = os.path.join(BDE, "triggers")
RESULTS = os.path.join(BDE, "results")
OUTPUT = os.path.join(BDE, "output")
SIDECAR_ROOT = os.path.join(OUTPUT, "monthly-analytics")
OS_DIR = os.path.join(HOME, "Documents/Claude/Projects/Valley Pawn OS/monthly-analytics")
LOG_DIR = os.path.join(OS_DIR, "logs")
STORES = ["CUL", "HAR", "LEX", "ROA", "WAY"]
WINDOW_KEYS = ["same-month-current", "same-month-prior", "ytd-current",
               "ytd-prior", "t12m-current", "t12m-prior"]
BRAVO_FLOOR = dt.date(2024, 6, 3)   # Bravo calendar floor (verified 2026-06-04)
POLL_SECS = 20
WINDOW_TIMEOUT_SECS = 15 * 60
MIN_GOOD_BYTES = 2048

_log_fh = None


def log(msg):
    line = "%s %s" % (dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), msg)
    print(line, flush=True)
    if _log_fh:
        _log_fh.write(line + "\n")
        _log_fh.flush()


def last_day(y, m):
    return dt.date(y, m, calendar.monthrange(y, m)[1])


def windows_for(report_month):
    y, m = report_month
    start = dt.date(y, m, 1)
    end = last_day(y, m)
    py = y - 1
    # last of report month minus 12 months + 1 day == first day of (m+1) of prior year
    t12_start = dt.date(py, m, 1) + dt.timedelta(days=calendar.monthrange(py, m)[1])
    t12p_start = dt.date(py - 1, t12_start.month, 1)
    t12p_end = last_day(py, m)
    clamped = None
    if t12p_start < BRAVO_FLOOR:
        clamped = t12p_start
        t12p_start = BRAVO_FLOOR
    return [
        ("same-month-current", start, end),
        ("same-month-prior", dt.date(py, m, 1), last_day(py, m)),
        ("ytd-current", dt.date(y, 1, 1), end),
        ("ytd-prior", dt.date(py, 1, 1), last_day(py, m)),
        ("t12m-current", t12_start, end),
        ("t12m-prior", t12p_start, t12p_end),
    ], clamped


def sidecar_ok(sidecar, key, store):
    p = os.path.join(sidecar, "%s_%s.xlsx" % (key, store))
    return os.path.isfile(p) and os.path.getsize(p) >= MIN_GOOD_BYTES


def host_path(win_path):
    """Convert the watcher's Windows-side path (Y:\\Documents\\...) to the Mac path."""
    p = win_path.replace("\\", "/")
    for prefix in ("Y:/Documents/", "Y:/documents/"):
        if p.startswith(prefix):
            return os.path.join(HOME, "Documents", p[len(prefix):])
    if p.startswith("/Users/"):
        return p
    # last resort: basename into output/
    return os.path.join(OUTPUT, os.path.basename(p))


def drop_trigger(tid, stores, start, end):
    payload = {
        "id": tid,
        "requested_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "reports": [{"name": "end-of-month", "stores": stores,
                     "date": "%s..%s" % (start.isoformat(), end.isoformat())}],
    }
    tmp = os.path.join(TRIGGERS, ".%s.tmp" % tid)
    with open(tmp, "w") as fh:
        json.dump(payload, fh, indent=2)
    os.replace(tmp, os.path.join(TRIGGERS, "%s.json" % tid))
    log("dropped trigger %s (%s..%s, %s)" % (tid, start, end, ",".join(stores)))


def wait_result(tid):
    rp = os.path.join(RESULTS, "%s.result.json" % tid)
    deadline = time.time() + WINDOW_TIMEOUT_SECS
    warned = False
    while time.time() < deadline:
        if os.path.isfile(rp):
            time.sleep(2)  # let the writer finish
            try:
                with open(rp, encoding="utf-8-sig") as fh:
                    return json.load(fh)
            except Exception as e:  # partial write — poll again
                log("result parse retry for %s: %s" % (tid, e))
        elif (not warned and time.time() > deadline - WINDOW_TIMEOUT_SECS + 180
              and os.path.isfile(os.path.join(TRIGGERS, "%s.json" % tid))):
            log("WARN trigger %s still unclaimed after 3 min — watcher may be busy or down" % tid)
            warned = True
        time.sleep(POLL_SECS)
    log("TIMEOUT waiting for %s" % tid)
    return None


def copy_cells(result, sidecar, key):
    """Copy each successful cell's output to the sidecar. Returns list of stores copied."""
    done = []
    for cell in result.get("cells", []):
        store = cell.get("store")
        if cell.get("status") != "success":
            log("  cell %s status=%s error=%s" % (store, cell.get("status"), cell.get("error")))
            continue
        src = host_path(cell.get("output_path", ""))
        if not (os.path.isfile(src) and os.path.getsize(src) >= MIN_GOOD_BYTES):
            log("  cell %s: output missing/too small at %s" % (store, src))
            continue
        dst = os.path.join(sidecar, "%s_%s.xlsx" % (key, store))
        shutil.copy2(src, dst)
        log("  copied %s -> %s (%d bytes)" % (os.path.basename(src), os.path.basename(dst), os.path.getsize(dst)))
        done.append(store)
    return done


def run_window(key, start, end, sidecar, stamp):
    missing = [s for s in STORES if not sidecar_ok(sidecar, key, s)]
    if not missing:
        log("window %s: sidecar already complete (5/5) — skipping" % key)
        return
    tid = "monthly-analytics-prestage-%s-%s" % (key, stamp)
    drop_trigger(tid, missing, start, end)
    res = wait_result(tid)
    if res:
        copy_cells(res, sidecar, key)
    still = [s for s in STORES if not sidecar_ok(sidecar, key, s)]
    if still:
        log("window %s: retrying %s" % (key, ",".join(still)))
        tid2 = tid + "-retry-1"
        drop_trigger(tid2, still, start, end)
        res2 = wait_result(tid2)
        if res2:
            copy_cells(res2, sidecar, key)
    final_missing = [s for s in STORES if not sidecar_ok(sidecar, key, s)]
    log("window %s: %d/5 staged%s" % (key, 5 - len(final_missing),
                                     (" (missing %s)" % ",".join(final_missing)) if final_missing else ""))


def write_status(report_month, wins, clamped, sidecar):
    y, m = report_month
    ym = "%04d-%02d" % (y, m)
    total = 0
    rows = []
    for key, s, e in wins:
        n = sum(1 for st in STORES if sidecar_ok(sidecar, key, st))
        total += n
        note = ""
        if key == "t12m-prior" and clamped:
            note = "  *(clamped — requested start %s, Bravo floor %s)*" % (clamped, BRAVO_FLOOR)
        rows.append("| %s | %s..%s | %d/5%s |" % (key, s, e, n, note))
    status = "COMPLETE 30/30" if total == 30 else ("PARTIAL %d/30" % total if total else "FAILED")
    files = []
    if os.path.isdir(sidecar):
        for f in sorted(os.listdir(sidecar)):
            if f.endswith(".xlsx"):
                files.append("- %s (%d bytes)" % (f, os.path.getsize(os.path.join(sidecar, f))))
    body = "\n".join([
        "# Monthly Analytics Prestage — %s" % ym,
        "",
        "**Status:** %s" % status,
        "**Runner:** bin/monthly_prestage_runner.py (native, launchd `com.valleypawn.monthly-prestage`) — no Claude session in the loop",
        "",
        "## Windows",
        "| Window | Range | CSVs |",
        "|---|---|---|",
    ] + rows + [
        "",
        "## Sidecar",
        "`%s/`" % sidecar,
        "",
    ] + files + [
        "",
        "## Notes",
        "Copy source = each cell's `output_path` from its result.json (authoritative), copied immediately after the window finished and before the next window was dropped.",
        "",
        "_Generated %s ET._" % dt.datetime.now().strftime("%Y-%m-%d %H:%M"),
    ])
    os.makedirs(OS_DIR, exist_ok=True)
    with open(os.path.join(OS_DIR, "%s Prestage.md" % ym), "w") as fh:
        fh.write(body + "\n")
    log("status: %s" % status)
    return total


def main():
    global _log_fh
    ap = argparse.ArgumentParser()
    ap.add_argument("--report-month", help="YYYY-MM (default: month ending today; requires tomorrow == 1st unless --force)")
    ap.add_argument("--force", action="store_true", help="skip the last-day-of-month gate")
    ap.add_argument("--dry-run", action="store_true", help="print windows and sidecar state, drop nothing")
    args = ap.parse_args()

    today = dt.date.today()
    if args.report_month:
        y, m = [int(x) for x in args.report_month.split("-")]
    else:
        if (today + dt.timedelta(days=1)).day != 1 and not args.force:
            print("SKIP: tomorrow is not the 1st (use --force or --report-month)")
            return 0
        y, m = today.year, today.month
    ym = "%04d-%02d" % (y, m)

    os.makedirs(LOG_DIR, exist_ok=True)
    _log_fh = open(os.path.join(LOG_DIR, "prestage-%s-%s.log" % (ym, dt.datetime.now().strftime("%Y%m%dT%H%M%S"))), "a")
    lock = os.path.join(LOG_DIR, ".runner-%s.lock" % ym)
    if os.path.exists(lock) and time.time() - os.path.getmtime(lock) < 3 * 3600:
        log("another runner holds %s (younger than 3h) — exiting" % lock)
        return 0
    with open(lock, "w") as fh:
        fh.write(str(os.getpid()))
    try:
        sidecar = os.path.join(SIDECAR_ROOT, ym)
        os.makedirs(sidecar, exist_ok=True)
        wins, clamped = windows_for((y, m))
        log("report month %s — %d windows — sidecar %s" % (ym, len(wins), sidecar))
        for key, s, e in wins:
            log("window %s: %s..%s" % (key, s, e))
        stamp = dt.datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
        if args.dry_run:
            for key, s, e in wins:
                log("  dry-run %s: %d/5 already staged" % (key, sum(1 for st in STORES if sidecar_ok(sidecar, key, st))))
            return 0
        for key, s, e in wins:
            run_window(key, s, e, sidecar, stamp)
        total = write_status((y, m), wins, clamped, sidecar)
        return 0 if total == 30 else 2
    finally:
        try:
            os.remove(lock)
        except OSError:
            pass


if __name__ == "__main__":
    sys.exit(main())
