#!/usr/bin/env python3
"""
Golden test for Job C (employee rankings) — stdlib only.

The fixture is NOT a byte-copy of a historical Slack post (unlike Job A's):
the ranked-list portion IS byte-identical to the real 2026-07-13 13:26 post
(verified 2026-07-26 — all 12 employees, exact order, exact $ figures,
including the cross-store aggregation for Martin Dowden and Andrew Clark),
but the "Company Total" line is an addition per the standing CLAUDE.md rule
that no historical post actually includes (same pattern as Job B).

Run: python3 tests/test_employee_rankings.py
"""
from __future__ import annotations
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
FIXTURES = Path(__file__).resolve().parent / "fixtures"
sys.path.insert(0, str(REPO))

from vpops import bravo, formats  # noqa: E402


def main() -> int:
    filename_date = "2026-07-01"  # employee-activity files regenerate in place; see module docstring
    files = bravo.locate_store_files(filename_date, "employee-activity.csv")
    missing = bravo.missing_stores(files)
    if missing:
        print(f"FAIL: missing stores: {missing}")
        return 1

    store_data = {s: formats.extract_employee_activity(p) for s, p in files.items()}
    got = formats.render_employee_rankings(store_data)
    expected = (FIXTURES / "employee_rankings_2026-07-13.txt").read_text()

    if got.strip() != expected.strip():
        import difflib
        print("FAIL — mismatch:")
        sys.stdout.writelines(difflib.unified_diff(
            expected.strip().splitlines(keepends=True), got.strip().splitlines(keepends=True),
            fromfile="expected", tofile="got",
        ))
        return 1

    print("PASS — ranked list matches the real 2026-07-13 post exactly; Company Total line correct.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
