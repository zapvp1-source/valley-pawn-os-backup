"""
bravo.py — locate Bravo Data Extraction pipeline output files, and (for
Job E) drop trigger JSON + wait for results.

Per BUILD_SPEC.md §4 file-access note: triggers/ and output/ are plain
local paths for a native process — a native launchd job (or this Bash-tool
session, verified to have the same direct access) reads/writes them
directly; the osascript bridge is only needed from the Claude-sandboxed
computer-use path, not here.
"""

from __future__ import annotations
import glob
import json
import os
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path

BRAVO_ROOT = Path("/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction")
OUTPUT_DIR = BRAVO_ROOT / "output"
TRIGGERS_DIR = BRAVO_ROOT / "triggers"
HEALTH_SCRIPT = BRAVO_ROOT / "bravo_ensure_healthy.sh"

STORES = ["CUL", "HAR", "LEX", "ROA", "WAY"]
STORE_NAMES = {
    "CUL": "Culpeper",
    "HAR": "Harrisonburg",
    "LEX": "Lexington",
    "ROA": "Roanoke",
    "WAY": "Waynesboro",
}

# 500 bytes is right for EOM XLSX exports (tens of KB) but too strict for
# the tiny single-row CSV cells (layaways.csv, loans-75-days-past-due.csv
# are legitimately ~100 bytes: header row + one data row). 20 bytes still
# catches a genuinely empty/truncated file while accepting a real 0-count
# result row (BUSINESS_OS Rule 8: 0 rows is a legitimate result, not a failure).
MIN_VALID_BYTES = 20


def latest_enddate(cell_suffix: str) -> str | None:
    """Given a cell filename suffix like 'end-of-month.xlsx', finds the most
    recent <DATE> present across output/*_<STORE>_<cell_suffix> files."""
    pattern = str(OUTPUT_DIR / f"*_{cell_suffix}")
    matches = sorted(glob.glob(pattern))
    if not matches:
        return None
    return os.path.basename(matches[-1]).split("_")[0]


def locate_store_files(enddate: str, cell_suffix: str) -> dict[str, Path | None]:
    """Returns {store: path_or_None} for a given date + cell suffix
    (e.g. 'end-of-month.xlsx', 'aged-inventory-summary.csv')."""
    out: dict[str, Path | None] = {}
    for store in STORES:
        p = OUTPUT_DIR / f"{enddate}_{store}_{cell_suffix}"
        if p.exists() and p.stat().st_size >= MIN_VALID_BYTES:
            out[store] = p
        else:
            out[store] = None
    return out


def latest_complete_date(cell_suffix: str) -> str | None:
    """Like latest_enddate(), but skips any date where fewer than all 5
    stores actually landed -- doesn't just check the single newest date
    and give up.

    Confirmed bug 2026-07-27 (first real unattended Monday run): Job E was
    mid-pull when Job D fired at its scheduled time. latest_enddate()
    returned today's date because ONE store's file existed, locate_store_
    files() then found the other 4 stores missing for THAT specific date,
    and the job gave up entirely -- even though a fully complete dataset
    from last night's pull was sitting right there one day older. A job
    firing on a schedule will always have some chance of racing an
    in-flight pull; falling back to the last known-complete date is the
    right behavior, not failing outright."""
    pattern = str(OUTPUT_DIR / f"*_{cell_suffix}")
    dates = sorted({os.path.basename(p).split("_")[0] for p in glob.glob(pattern)}, reverse=True)
    for d in dates:
        if not missing_stores(locate_store_files(d, cell_suffix)):
            return d
    return None


def latest_store_files_by_mtime(cell_suffix: str) -> dict[str, Path | None]:
    """Same shape as locate_store_files, but finds each store's most
    recently MODIFIED file matching *_<STORE>_<cell_suffix>, ignoring the
    filename's date prefix entirely.

    Needed because the date-prefix convention isn't consistent across cells:
    end-of-month's AHK handler names its file by the END date of a passed
    range ('2026-07-25_CUL_end-of-month.xlsx' for a '2026-07-01..2026-07-25'
    request), but employee-activity's handler uses the RAW range string
    verbatim ('2026-07-01..2026-07-25_CUL_employee-activity.csv') — so
    locate_store_files()'s single-date assumption silently misses fresh
    employee-activity pulls (confirmed 2026-07-26: a fresh pull sat
    unnoticed next to a 13-day-stale same-store file with a different name
    shape). mtime is the one thing that's always reliable regardless of
    what the AHK handler decided to call the file."""
    out: dict[str, Path | None] = {}
    for store in STORES:
        pattern = str(OUTPUT_DIR / f"*_{store}_{cell_suffix}")
        matches = [p for p in glob.glob(pattern) if os.path.getsize(p) >= MIN_VALID_BYTES]
        out[store] = Path(max(matches, key=os.path.getmtime)) if matches else None
    return out


def missing_stores(files: dict[str, Path | None]) -> list[str]:
    return [s for s, p in files.items() if p is None]


def ensure_healthy(target_store: str = "CUL", timeout_s: int = 900) -> bool:
    """Runs the existing bravo_ensure_healthy.sh gate. Returns True on PASS.

    900s default (not the original 300s): a worst-case recovery cycle
    (gentle recover fail -> guarded kill -> relaunch -> re-recover) has been
    observed taking 6-9 minutes end to end. A too-short timeout here doesn't
    just fail fast — subprocess.run()'s default timeout handling only kills
    the immediate child (this wrapper script), not the bash/AHK/prlctl
    grandchildren it spawns, so the ORPHANED recovery process keeps running
    unsupervised in the background after we've already given up and moved
    on. That's strictly worse than waiting: it can leave Bravo in a
    half-relaunched state (confirmed 2026-07-26 — a duplicate Bravo.exe
    instance from an orphaned relaunch) for the NEXT caller to trip over.
    start_new_session=True + killing the whole process group on timeout
    ensures a real timeout actually stops everything, not just this wrapper.
    """
    import signal
    try:
        proc = subprocess.Popen(
            ["bash", str(HEALTH_SCRIPT), target_store],
            cwd=str(BRAVO_ROOT), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, start_new_session=True,
        )
        try:
            proc.communicate(timeout=timeout_s)
            return proc.returncode == 0
        except subprocess.TimeoutExpired:
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
                proc.communicate(timeout=10)
            except Exception:
                try:
                    os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
                except Exception:
                    pass
            return False
    except Exception:
        return False


def drop_trigger(trigger_id: str, reports: list) -> Path:
    """reports: [{"name": cell, "stores": [...], "date": "YYYY-MM-DD" or "A..B"}].
    Writes directly to triggers/ (see module docstring on why no osascript
    bridge is needed here)."""
    payload = {
        "id": trigger_id,
        "requested_at": datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z"),
        "reports": reports,
    }
    path = TRIGGERS_DIR / f"{trigger_id}.json"
    path.write_text(json.dumps(payload))
    return path


def wait_for_cell(date_str: str, cell_suffix: str, stores: list = None, timeout_s: int = 1500, poll_s: int = 15) -> list:
    """Polls output/ until every store's file for this cell+date exists (or
    timeout). Returns the list of stores still missing (empty = success)."""
    stores = stores or STORES
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        files = locate_store_files(date_str, cell_suffix)
        missing = [s for s in stores if files[s] is None]
        if not missing:
            return []
        time.sleep(poll_s)
    files = locate_store_files(date_str, cell_suffix)
    return [s for s in stores if files[s] is None]


def wait_for_cell_by_mtime(cell_suffix: str, since_ts: float, stores: list = None, timeout_s: int = 1500, poll_s: int = 15) -> list:
    """Like wait_for_cell(), but for cells whose AHK handler names output
    files by the raw requested date range rather than a single end-date
    (confirmed for employee-activity — see latest_store_files_by_mtime's
    docstring). date-prefix polling can never match these files' names, so
    it polls by "does this store have a file newer than since_ts" instead.
    Found 2026-07-27: job_trigger_dropper's own wait loop was stuck the
    entire first real Monday run waiting on a file it could never find by
    name, even though the data had already landed."""
    stores = stores or STORES
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        files = latest_store_files_by_mtime(cell_suffix)
        missing = [s for s in stores if files[s] is None or os.path.getmtime(files[s]) < since_ts]
        if not missing:
            return []
        time.sleep(poll_s)
    files = latest_store_files_by_mtime(cell_suffix)
    return [s for s in stores if files[s] is None or os.path.getmtime(files[s]) < since_ts]


GOOGLE_SHEETS_LINKS = {
    # doc_id read from the .gsheet shortcut file's JSON — these shortcuts
    # are Google Drive metadata pointers, not the actual sheet content.
    "aged-inventory": "https://docs.google.com/spreadsheets/d/1aEatyu3YMfJcjIfcaIVHU9Lq8jOUtpH0Jd77LGDdvPM/edit",
}

# --- FPD shared archive (BUILD_SPEC_WAVE2.md Hard Rule #9) ---
# Shared state with the legacy Monday-combined path: append-only, dedupe by
# ticket_number, never rewrite or reorder existing rows. Dedupe is the
# concurrency-safety mechanism (both this job and any manually-run legacy
# task can append without colliding) -- preserve it exactly.
FPD_ARCHIVE_PATH = Path("/Users/joshuadavis/Documents/Claude/Scheduled/_fpd-archive/fpd-history.csv")
FPD_ARCHIVE_FIELDS = ["first_seen_date", "store", "ticket_number", "category", "full_description", "loan_amount"]


def read_fpd_archive() -> list:
    """Returns the archive as a list of dicts, in file order (oldest first).
    Empty list if the file doesn't exist yet."""
    import csv as csv_mod
    if not FPD_ARCHIVE_PATH.exists():
        return []
    with open(FPD_ARCHIVE_PATH, newline="", encoding="latin-1") as f:
        return list(csv_mod.DictReader(f))


def append_fpd_archive(today_str: str, cohort_rows: dict) -> int:
    """cohort_rows: {store: [{'ticket_number', 'category', 'full_description',
    'loan_amount'}, ...]}. Appends only tickets not already present (by
    ticket_number) — existing rows are never touched. Returns count appended."""
    import csv as csv_mod
    existing = read_fpd_archive()
    seen = {r["ticket_number"] for r in existing}
    new_rows = []
    for store, tickets in cohort_rows.items():
        for t in tickets:
            if t["ticket_number"] in seen:
                continue
            seen.add(t["ticket_number"])
            new_rows.append({
                "first_seen_date": today_str, "store": store,
                "ticket_number": t["ticket_number"], "category": t["category"],
                "full_description": t["full_description"], "loan_amount": t["loan_amount"],
            })
    if not new_rows:
        return 0
    write_header = not FPD_ARCHIVE_PATH.exists()
    with open(FPD_ARCHIVE_PATH, "a", newline="", encoding="latin-1") as f:
        writer = csv_mod.DictWriter(f, fieldnames=FPD_ARCHIVE_FIELDS)
        if write_header:
            writer.writeheader()
        for r in new_rows:
            writer.writerow(r)
    return len(new_rows)


# --- Job I: Monthly Analytics (BUILD_SPEC_WAVE2.md §3) ---
# `company-kpis` is a single ALL-stores file per end-date, unlike the
# per-store cells above. Several of the 6 YoY windows share the same
# end-date (all 3 "current" windows end on the report month's last day; all
# 3 "prior" windows end on that same day one year back) -- pulling them
# back-to-back would silently overwrite output/{enddate}_ALL_company-kpis.xlsx
# before the next window's result is even read. job_monthly_prestage.py
# copies each window's result to a window-tagged sidecar immediately after
# it lands, before dropping the next trigger -- same pattern the legacy
# monthly-analytics-prestage/SKILL.md uses for the per-store EOM cell.
MONTHLY_SIDECAR_DIR = Path(__file__).resolve().parent.parent / "data" / "monthly-analytics"
BRAVO_CALENDAR_FLOOR = "2024-06-03"  # verified 2026-06-04, per monthly-analytics-prestage/SKILL.md


def locate_company_kpis_file(enddate: str) -> Path | None:
    p = OUTPUT_DIR / f"{enddate}_ALL_company-kpis.xlsx"
    return p if p.exists() and p.stat().st_size >= MIN_VALID_BYTES else None


def wait_for_company_kpis(enddate: str, since_ts: float, timeout_s: int = 720, poll_s: int = 18) -> bool:
    """Polls for output/{enddate}_ALL_company-kpis.xlsx, requiring it be
    newer than since_ts (guards against reading a stale file left over from
    an earlier window that happened to share the same end-date)."""
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        p = locate_company_kpis_file(enddate)
        if p is not None and p.stat().st_mtime >= since_ts:
            return True
        time.sleep(poll_s)
    p = locate_company_kpis_file(enddate)
    return p is not None and p.stat().st_mtime >= since_ts


def copy_company_kpis_to_sidecar(enddate: str, window_key: str, month_key: str) -> Path | None:
    """Copies the just-landed output/{enddate}_ALL_company-kpis.xlsx to
    data/monthly-analytics/{month_key}/{window_key}.xlsx. Returns the
    sidecar path, or None if the source file isn't there."""
    import shutil
    src = locate_company_kpis_file(enddate)
    if src is None:
        return None
    dest_dir = MONTHLY_SIDECAR_DIR / month_key
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / f"{window_key}.xlsx"
    shutil.copyfile(src, dest)
    return dest


def _last_day_of_month(year: int, month: int):
    if month == 12:
        next_first = datetime(year + 1, 1, 1)
    else:
        next_first = datetime(year, month + 1, 1)
    return next_first - timedelta(days=1)


def _add_months(year: int, month: int, delta: int) -> tuple[int, int]:
    total = (year * 12 + (month - 1)) + delta
    ny, nm = divmod(total, 12)
    return ny, nm + 1


def compute_monthly_windows(report_month_start: datetime) -> dict:
    """report_month_start: a datetime for the 1st of the report month (the
    month that just ended). Returns a flat dict of 6 (start, end) date-string
    tuples keyed same_month_current/prior, ytd_current/prior, t12m_current/
    prior, plus t12m_prior_clamped (bool) and t12m_prior_note (str, empty if
    not clamped). Mirrors monthly-analytics-prestage/SKILL.md's window table."""
    Y, M = report_month_start.year, report_month_start.month
    fmt = "%Y-%m-%d"

    month_end = _last_day_of_month(Y, M)
    same_month_current = (report_month_start, month_end)

    prior_month_end = _last_day_of_month(Y - 1, M)
    same_month_prior = (datetime(Y - 1, M, 1), prior_month_end)

    ytd_current = (datetime(Y, 1, 1), month_end)
    ytd_prior = (datetime(Y - 1, 1, 1), prior_month_end)

    t12m_start_y, t12m_start_m = _add_months(Y, M, -11)
    t12m_current = (datetime(t12m_start_y, t12m_start_m, 1), month_end)

    t12m_prior_start_y, t12m_prior_start_m = _add_months(Y - 1, M, -11)
    t12m_prior_start = datetime(t12m_prior_start_y, t12m_prior_start_m, 1)
    floor_dt = datetime.strptime(BRAVO_CALENDAR_FLOOR, fmt)
    clamped = t12m_prior_start < floor_dt
    actual_t12m_prior_start = floor_dt if clamped else t12m_prior_start
    if actual_t12m_prior_start > prior_month_end:
        raise ValueError(
            f"T12M Prior window is entirely before the Bravo calendar floor "
            f"({BRAVO_CALENDAR_FLOOR}) for report month {Y}-{M:02d} — this "
            f"function is only meant for report months from 2025 onward."
        )
    t12m_prior = (actual_t12m_prior_start, prior_month_end)

    note = ""
    if clamped:
        variance_days = (floor_dt - t12m_prior_start).days
        note = f"T12M Prior start = {BRAVO_CALENDAR_FLOOR} (Bravo calendar floor) — {variance_days}-day variance from the full 12-month window."

    def s(d):
        return d.strftime(fmt)

    return {
        "same_month_current": (s(same_month_current[0]), s(same_month_current[1])),
        "same_month_prior": (s(same_month_prior[0]), s(same_month_prior[1])),
        "ytd_current": (s(ytd_current[0]), s(ytd_current[1])),
        "ytd_prior": (s(ytd_prior[0]), s(ytd_prior[1])),
        "t12m_current": (s(t12m_current[0]), s(t12m_current[1])),
        "t12m_prior": (s(t12m_prior[0]), s(t12m_prior[1])),
        "t12m_prior_clamped": clamped,
        "t12m_prior_note": note,
    }


# --- Job J: Monthly Gold Trend (BUILD_SPEC_WAVE2.md §4) ---
# `scrap-refining-gold` is an EXISTING, already-registered pipeline cell
# (confirmed 2026-07-27 in both bravo_watcher.ahk and bravo_export.ahk,
# built 2026-07-18..23) -- BUILD_SPEC_WAVE2.md's claim that "no pipeline
# handler exists" for J-0 was stale. Output is one CSV per store per year:
# output/{YEAR}_{STORE}_scrap-refining-gold.csv.
GOLD_DWT_HISTORY_PATH = Path(__file__).resolve().parent.parent / "data" / "gold_dwt_history.csv"
GOLD_DWT_HISTORY_FIELDS = ["store", "year_month", "dwt", "source", "recorded_at"]


def locate_scrap_refining_gold_file(store: str, year: int) -> Path | None:
    p = OUTPUT_DIR / f"{year}_{store}_scrap-refining-gold.csv"
    return p if p.exists() and p.stat().st_size >= MIN_VALID_BYTES else None


def wait_for_scrap_refining_gold(stores: list, year: int, since_ts: float, timeout_s: int = 900, poll_s: int = 20) -> list:
    """Polls output/{year}_{store}_scrap-refining-gold.csv for each store,
    requiring mtime >= since_ts (same freshness-only pattern as
    wait_for_company_kpis -- the file is per-store-per-YEAR, not per-request,
    so a plain existence check can't tell a stale file from a fresh pull).
    Returns the list of stores still missing (empty = success)."""
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        missing = [s for s in stores if (p := locate_scrap_refining_gold_file(s, year)) is None or p.stat().st_mtime < since_ts]
        if not missing:
            return []
        time.sleep(poll_s)
    return [s for s in stores if (p := locate_scrap_refining_gold_file(s, year)) is None or p.stat().st_mtime < since_ts]


def read_gold_dwt_history() -> list:
    """Returns the archive as a list of dicts, oldest first. Empty list if
    the file doesn't exist yet."""
    import csv as csv_mod
    if not GOLD_DWT_HISTORY_PATH.exists():
        return []
    with open(GOLD_DWT_HISTORY_PATH, newline="", encoding="latin-1") as f:
        return list(csv_mod.DictReader(f))


def append_gold_dwt_history(rows: list) -> int:
    """rows: [{'store','year_month','dwt','source'}]. Append-only, dedupe by
    (store, year_month) -- a rerun for an already-recorded store+month is
    skipped rather than duplicated (same pattern as the FPD archive's
    ticket-level dedup, just keyed on the monthly aggregate instead)."""
    import csv as csv_mod
    from datetime import datetime as _dt
    existing = read_gold_dwt_history()
    seen = {(r["store"], r["year_month"]) for r in existing}
    new_rows = []
    for r in rows:
        key = (r["store"], r["year_month"])
        if key in seen:
            continue
        seen.add(key)
        new_rows.append({
            "store": r["store"], "year_month": r["year_month"], "dwt": r["dwt"],
            "source": r.get("source", ""), "recorded_at": _dt.now().isoformat(),
        })
    if not new_rows:
        return 0
    GOLD_DWT_HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    write_header = not GOLD_DWT_HISTORY_PATH.exists()
    with open(GOLD_DWT_HISTORY_PATH, "a", newline="", encoding="latin-1") as f:
        writer = csv_mod.DictWriter(f, fieldnames=GOLD_DWT_HISTORY_FIELDS)
        if write_header:
            writer.writeheader()
        for r in new_rows:
            writer.writerow(r)
    return len(new_rows)
