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
from datetime import datetime
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


GOOGLE_SHEETS_LINKS = {
    # doc_id read from the .gsheet shortcut file's JSON — these shortcuts
    # are Google Drive metadata pointers, not the actual sheet content.
    "aged-inventory": "https://docs.google.com/spreadsheets/d/1aEatyu3YMfJcjIfcaIVHU9Lq8jOUtpH0Jd77LGDdvPM/edit",
}
