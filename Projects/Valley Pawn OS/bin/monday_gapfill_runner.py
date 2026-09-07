#!/usr/bin/env python3
"""
monday_gapfill_runner.py — re-pull the Monday-compile cells that failed in the
Sunday combined run, so Monday morning's ops posts have all 5 stores.

WHY THIS EXISTS (2026-09-05)
`monday-bravo-combined-run` drops ONE 30-cell trigger on Sunday evening. When
individual cells fail there is no retry: the CSV never lands, and Monday's
compile either posts a partial table (the old behaviour, which produced the
"pipeline cell failed" notes staff saw all August) or — since Completeness
Gate v2 was added 2026-08-31 — correctly posts nothing at all. Either way the
channel does not get its report.

The 2026-08-30 run is the reference case: 10 of 30 cells failed, and the errors
were all stranded-UI-state symptoms, not data problems —
  5x "EnsureStore failed"        (Bravo dropped to the login screen mid-run)
  1x "BackToDashboard could not return Bravo to Dashboard"
  2x aged-inventory UIA timing   ("element not found: Ok", "File path LayoutItem not found")
  1x "Grid walk truncated: captured 22 of 44 rows" (handler correctly refused a partial grid)
Every one of those is the documented recover-Bravo-first class (BRAVO_KNOWN_ISSUES.md):
a watcher restart plus a fresh claim clears it. Cells that pass on the retry are
real data; cells that fail twice are a genuine problem for a human.

WHAT IT DOES
 1. Finds the most recent monday-bravo-combined-*.result.json (or --date).
 2. Collects every cell whose status != "success", skipping any whose output CSV
    already exists and is non-trivial (another task may have back-filled it).
 3. Restarts the Bravo watcher once (_restart_watcher_v2.ps1 via prlctl) — the
    documented first step for the EnsureStore/BackToDashboard class. Skipped
    with --no-restart, and skipped automatically if the queue is busy.
 4. Re-drops ONE trigger containing only the failed cells, waits for its result.
 5. One more focused retry for whatever still failed.
 6. Writes Valley Pawn OS/monday-gapfill/{DATE}.md and exits.
Silent by design: no Slack, no DM. The Monday compile and postcheck own
notification. Exit 0 = nothing left failing, 2 = something still failing.

ADDITIVE: reads result.json, writes triggers, restarts the watcher. Never edits
a handler, the watcher source, a SKILL.md, or any existing output CSV.
"""
import argparse
import datetime as dt
import glob
import json
import os
import re
import subprocess
import sys
import time

HOME = os.path.expanduser("~")
BDE = os.path.join(HOME, "Documents/Claude/Projects/Bravo Data Extraction")
TRIGGERS = os.path.join(BDE, "triggers")
CLAIMED = os.path.join(TRIGGERS, "claimed")
RESULTS = os.path.join(BDE, "results")
OUTPUT = os.path.join(BDE, "output")
OS_DIR = os.path.join(HOME, "Documents/Claude/Projects/Valley Pawn OS/monday-gapfill")
VM_UUID = "{7dc84f03-4e68-4f43-9596-bf8a7dfb8e0a}"
RESTART_PS1 = r"Y:\Documents\Claude\Projects\Bravo Data Extraction\_restart_watcher_v2.ps1"
POLL_SECS = 20
TIMEOUT_SECS = 45 * 60          # the watcher's own per-trigger cap
MIN_GOOD_BYTES = 20             # only rejects 0-byte / truncated stubs, NOT small valid reports

_log_fh = None


def _release(lock):
    try:
        os.remove(lock)
    except OSError:
        pass


def log(msg):
    line = "%s %s" % (dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), msg)
    print(line, flush=True)
    if _log_fh:
        _log_fh.write(line + "\n")
        _log_fh.flush()


def load_result(path):
    with open(path, encoding="utf-8-sig") as fh:
        return json.load(fh)


def newest_combined_result(date=None):
    if date:
        p = os.path.join(RESULTS, "monday-bravo-combined-%s.result.json" % date)
        return p if os.path.isfile(p) else None
    files = sorted(glob.glob(os.path.join(RESULTS, "monday-bravo-combined-*.result.json")))
    return files[-1] if files else None


def host_path(win_path):
    p = (win_path or "").replace("\\", "/")
    for prefix in ("Y:/Documents/", "Y:/documents/"):
        if p.startswith(prefix):
            return os.path.join(HOME, "Documents", p[len(prefix):])
    if p.startswith("/Users/"):
        return p
    return os.path.join(OUTPUT, os.path.basename(p)) if p else ""


def csv_present(report, store, date):
    """A cell is already covered if its output exists and holds a real result.

    "Real result" is header + at least one row — NOT a byte-size floor. Fixed
    2026-09-06 after the first live run: the summary-style reports write tiny
    files (loans-75-days-past-due for CUL is 51 bytes: "store,date,count,
    dollar_sum" / "CUL,2026-08-30,0,0.0"), and an earlier 200-byte floor
    classified all five stores' perfectly valid files as missing — which would
    have re-pulled cells that had already succeeded, every run, forever.
    A zero result is a REAL result here: monday-bravo-combined-compile says so
    explicitly ("loans-75-days-past-due, layaways, and fpd-cohort legitimately
    return 0/empty as a real result"), and Culpeper genuinely ran the whole of
    August with zero loans past 75 days.
    """
    for name in ("%s_%s_%s.csv" % (date, store, report),
                 "%s_%s_%s.xlsx" % (date, store, report)):
        p = os.path.join(OUTPUT, name)
        if not os.path.isfile(p) or os.path.getsize(p) < MIN_GOOD_BYTES:
            continue
        if p.endswith(".xlsx"):
            return p
        try:
            with open(p, encoding="utf-8-sig", errors="ignore") as fh:
                rows = [ln for ln in fh.read().splitlines() if ln.strip()]
            if len(rows) >= 2:
                return p
            log("  %s/%s output has header only (%d line) — treating as missing"
                % (report, store, len(rows)))
        except Exception as e:
            log("  %s/%s output unreadable (%s) — treating as missing" % (report, store, e))
    return None


def queue_busy():
    pending = glob.glob(os.path.join(TRIGGERS, "*.json"))
    claimed = [f for f in glob.glob(os.path.join(CLAIMED, "*.json"))
               if time.time() - os.path.getmtime(f) < 2 * 3600]
    return pending or claimed


def restart_watcher():
    log("restarting watcher (documented first step for EnsureStore/BackToDashboard failures)")
    try:
        subprocess.run(["prlctl", "exec", VM_UUID, "--current-user", "powershell",
                        "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", RESTART_PS1],
                       capture_output=True, timeout=300)
    except Exception as e:
        log("  watcher restart call errored (continuing): %s" % e)
    logp = os.path.join(BDE, "logs/_restart_watcher_v2.log")
    try:
        tail = open(logp, errors="ignore").read()[-1200:]
        for line in tail.splitlines():
            if "step3:" in line:
                log("  " + line.strip())
                return "PASS" in line
    except Exception:
        pass
    return False


def drop_trigger(tid, cells):
    """cells: list of (report, store, date) — grouped into one report entry per (report, date)."""
    grouped = {}
    for report, store, date in cells:
        grouped.setdefault((report, date), []).append(store)
    payload = {
        "id": tid,
        "requested_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "reports": [{"name": r, "stores": sorted(set(s)), "date": d}
                    for (r, d), s in sorted(grouped.items())],
    }
    tmp = os.path.join(TRIGGERS, ".%s.tmp" % tid)
    with open(tmp, "w") as fh:
        json.dump(payload, fh, indent=2)
    os.replace(tmp, os.path.join(TRIGGERS, "%s.json" % tid))
    log("dropped %s with %d cell(s): %s" % (
        tid, len(cells), ", ".join("%s/%s" % (r, s) for r, s, _ in cells)))


def wait_result(tid):
    rp = os.path.join(RESULTS, "%s.result.json" % tid)
    deadline = time.time() + TIMEOUT_SECS
    while time.time() < deadline:
        if os.path.isfile(rp):
            time.sleep(2)
            try:
                return load_result(rp)
            except Exception as e:
                log("  result parse retry: %s" % e)
        time.sleep(POLL_SECS)
    log("TIMEOUT waiting for %s" % tid)
    return None


def failed_cells_from(result, source_date):
    out = []
    for c in result.get("cells", []):
        if c.get("status") == "success":
            continue
        report, store = c.get("report"), c.get("store")
        date = c.get("date") or source_date
        if csv_present(report, store, date):
            log("  %s/%s already has output on disk — skipping" % (report, store))
            continue
        out.append((report, store, date, (c.get("error") or "")[:160]))
    return out


def write_status(source, source_date, first, after1, after2, restarted):
    os.makedirs(OS_DIR, exist_ok=True)
    lines = [
        "# Monday combined-run gap-fill — %s" % source_date,
        "",
        "**Source result:** `%s`" % os.path.basename(source),
        "**Watcher restarted first:** %s" % ("yes (PASS)" if restarted else "no / not confirmed"),
        "**Failed cells found:** %d" % len(first),
        "**Still failing after retry 1:** %d" % len(after1),
        "**Still failing after retry 2:** %d" % len(after2),
        "",
        "## Cells this run tried to recover",
        "| report | store | date | original error |",
        "|---|---|---|---|",
    ]
    for r, s, d, e in first:
        lines.append("| %s | %s | %s | %s |" % (r, s, d, e.replace("|", "/")))
    if after2:
        lines += ["", "## STILL MISSING after two retries — needs a human",
                  "These reports will be withheld from their channels by Completeness Gate v2:"]
        for r, s, d, _ in after2:
            lines.append("- %s / %s (%s)" % (r, s, d))
    else:
        lines += ["", "All cells recovered — Monday's compile has a complete 5-store set."]
    lines += ["", "_Generated %s ET by bin/monday_gapfill_runner.py._"
              % dt.datetime.now().strftime("%Y-%m-%d %H:%M")]
    with open(os.path.join(OS_DIR, "%s.md" % source_date), "w") as fh:
        fh.write("\n".join(lines) + "\n")


def main():
    global _log_fh
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", help="YYYY-MM-DD of the combined run to repair (default: newest)")
    ap.add_argument("--no-restart", action="store_true", help="skip the watcher restart")
    ap.add_argument("--dry-run", action="store_true", help="list failed cells, drop nothing")
    args = ap.parse_args()

    source = newest_combined_result(args.date)
    if not source:
        print("no monday-bravo-combined result.json found")
        return 1
    m = re.search(r"monday-bravo-combined-(\d{4}-\d{2}-\d{2})", source)
    source_date = m.group(1) if m else dt.date.today().isoformat()

    os.makedirs(OS_DIR, exist_ok=True)
    _log_fh = open(os.path.join(OS_DIR, "gapfill-%s.log" % source_date), "a")

    # Single-runner lock (added 2026-09-06). The first live run raced itself:
    # the scheduled task launched at 01:00:58 and again at 01:01:35, so two
    # runners each dropped their own repair trigger and each waited on the
    # other's, producing a spurious 45-min TIMEOUT and a duplicate retry-2.
    # The outcome was still correct (all 9 cells recovered) but it doubled the
    # queue time. Same guard the prestage runner already carries.
    lock = os.path.join(OS_DIR, ".runner-%s.lock" % source_date)
    if os.path.exists(lock) and time.time() - os.path.getmtime(lock) < 3 * 3600:
        log("another gap-fill runner holds %s (younger than 3h) — exiting" % lock)
        return 0
    with open(lock, "w") as fh:
        fh.write(str(os.getpid()))

    log("source: %s" % source)

    result = load_result(source)
    first = failed_cells_from(result, source_date)
    if not first:
        log("no failed cells — nothing to do")
        write_status(source, source_date, [], [], [], False)
        _release(lock)
        return 0
    log("%d cell(s) need re-pulling" % len(first))
    for r, s, d, e in first:
        log("  %s/%s (%s): %s" % (r, s, d, e))
    if args.dry_run:
        _release(lock)
        return 0

    restarted = False
    if not args.no_restart:
        if queue_busy():
            log("queue busy — skipping the watcher restart (never restart mid-claim)")
        else:
            restarted = restart_watcher()

    stamp = dt.datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    tid = "monday-gapfill-%s-%s" % (source_date, stamp)
    drop_trigger(tid, [(r, s, d) for r, s, d, _ in first])
    res1 = wait_result(tid)
    after1 = failed_cells_from(res1, source_date) if res1 else first
    log("after retry 1: %d still failing" % len(after1))

    after2 = after1
    if after1:
        tid2 = tid + "-retry-2"
        drop_trigger(tid2, [(r, s, d) for r, s, d, _ in after1])
        res2 = wait_result(tid2)
        after2 = failed_cells_from(res2, source_date) if res2 else after1
        log("after retry 2: %d still failing" % len(after2))

    write_status(source, source_date, first, after1, after2, restarted)
    _release(lock)
    return 0 if not after2 else 2


if __name__ == "__main__":
    sys.exit(main())
