#!/usr/bin/env python3
"""
Golden test for the 3 bugs found and fixed during the first real unattended
Monday run (2026-07-27) — proves the fixes hold, rather than just asserting
it in a comment. Uses a temp scratch directory (monkey-patches
vpops.bravo.OUTPUT_DIR) so it never touches real Bravo output/.

Covers:
1. latest_complete_date() falls back past an incomplete "latest" date to
   the newest date where all 5 stores actually landed (the race-condition
   bug: Job D firing while Job E's pull was still in flight).
2. latest_store_files_by_mtime() finds range-named files (employee-activity's
   filename convention) regardless of the date-prefix.
3. wait_for_cell_by_mtime() correctly distinguishes an old stale file from
   a genuinely fresh one landed after a given reference timestamp.

Run: python3 tests/test_bravo_freshness.py
"""
from __future__ import annotations
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from vpops import bravo  # noqa: E402


def with_scratch_dir(fn):
    """Runs fn with vpops.bravo.OUTPUT_DIR pointed at a fresh temp dir,
    restoring the real path afterward no matter what."""
    real_output_dir = bravo.OUTPUT_DIR
    scratch = Path(tempfile.mkdtemp(prefix="vpops_test_"))
    bravo.OUTPUT_DIR = scratch
    try:
        return fn(scratch)
    finally:
        bravo.OUTPUT_DIR = real_output_dir
        shutil.rmtree(scratch, ignore_errors=True)


def touch(path: Path, content: str = "x" * 50, mtime: float = None):
    path.write_text(content)
    if mtime is not None:
        os.utime(path, (mtime, mtime))


def test_latest_complete_date_falls_back():
    """The exact 2026-07-27 scenario: today's pull is 4/5 done, yesterday's
    is fully complete. Must return yesterday, not today."""
    def body(scratch):
        # Yesterday: all 5 stores complete.
        for s in bravo.STORES:
            touch(scratch / f"2026-07-26_{s}_loans-75-days-past-due.csv")
        # Today: only 4 of 5 (WAY missing) -- exactly what happened live.
        for s in ["CUL", "HAR", "LEX", "ROA"]:
            touch(scratch / f"2026-07-27_{s}_loans-75-days-past-due.csv")

        return bravo.latest_complete_date("loans-75-days-past-due.csv")

    result = with_scratch_dir(body)
    ok = result == "2026-07-26"
    print(f"  latest_complete_date falls back to complete date: got {result!r}, expected '2026-07-26' -- {'PASS' if ok else 'FAIL'}")
    return ok


def test_latest_complete_date_uses_today_once_complete():
    """Once the 5th store lands, today should immediately become the
    answer -- this isn't just 'always prefer yesterday'."""
    def body(scratch):
        for s in bravo.STORES:
            touch(scratch / f"2026-07-26_{s}_loans-75-days-past-due.csv")
        for s in bravo.STORES:  # all 5 today too
            touch(scratch / f"2026-07-27_{s}_loans-75-days-past-due.csv")
        return bravo.latest_complete_date("loans-75-days-past-due.csv")

    result = with_scratch_dir(body)
    ok = result == "2026-07-27"
    print(f"  latest_complete_date prefers today once it's actually complete: got {result!r} -- {'PASS' if ok else 'FAIL'}")
    return ok


def test_mtime_locator_finds_range_named_files():
    """employee-activity's real convention: filename is the raw requested
    range, not a single end-date. Must still be found."""
    def body(scratch):
        for s in bravo.STORES:
            touch(scratch / f"2026-07-01..2026-07-26_{s}_employee-activity.csv")
        files = bravo.latest_store_files_by_mtime("employee-activity.csv")
        return files

    files = with_scratch_dir(body)
    ok = all(files.get(s) is not None for s in bravo.STORES)
    print(f"  latest_store_files_by_mtime finds range-named files: {'PASS' if ok else 'FAIL'} ({files})")
    return ok


def test_wait_for_cell_by_mtime_distinguishes_stale_vs_fresh():
    """A file from yesterday's pull should NOT count as satisfying a
    'landed after this run started' check -- otherwise job_trigger_dropper
    would falsely believe a stale file was this run's fresh pull."""
    def body(scratch):
        old_ts = time.time() - 3600  # 1 hour ago
        for s in bravo.STORES:
            touch(scratch / f"2026-07-01..2026-07-26_{s}_employee-activity.csv", mtime=old_ts)

        since_ts = time.time() - 60  # "this run" started 1 minute ago
        # All files are OLDER than since_ts -> should report all 5 as still missing.
        remaining_before = bravo.wait_for_cell_by_mtime("employee-activity.csv", since_ts=since_ts, timeout_s=1, poll_s=1)

        # Now one store's file lands fresh (after since_ts).
        touch(scratch / f"2026-07-01..2026-07-27_CUL_employee-activity.csv", mtime=time.time())
        remaining_after = bravo.wait_for_cell_by_mtime("employee-activity.csv", since_ts=since_ts, stores=["CUL"], timeout_s=1, poll_s=1)

        return remaining_before, remaining_after

    remaining_before, remaining_after = with_scratch_dir(body)
    ok = set(remaining_before) == set(bravo.STORES) and remaining_after == []
    print(f"  wait_for_cell_by_mtime distinguishes stale vs fresh: before={remaining_before}, after={remaining_after} -- {'PASS' if ok else 'FAIL'}")
    return ok


def main() -> int:
    print("=== Bravo freshness/race-condition fixes (2026-07-27) ===")
    results = [
        test_latest_complete_date_falls_back(),
        test_latest_complete_date_uses_today_once_complete(),
        test_mtime_locator_finds_range_named_files(),
        test_wait_for_cell_by_mtime_distinguishes_stale_vs_fresh(),
    ]
    ok = all(results)
    print("\n" + ("ALL PASS" if ok else "SOME FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
