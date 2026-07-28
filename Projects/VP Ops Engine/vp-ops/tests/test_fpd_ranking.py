#!/usr/bin/env python3
"""
Golden test for Job H (FPD ranking) — stdlib only.

Verified byte-for-byte against the real 2026-07-22 post (BUILD_SPEC_WAVE2.md
captured it verbatim; independently confirmed here against real CSVs + the
real archive file, not just copied from the spec).

Run: python3 tests/test_fpd_ranking.py
"""
from __future__ import annotations
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
FIXTURES = Path(__file__).resolve().parent / "fixtures"
sys.path.insert(0, str(REPO))

from vpops import bravo, formats  # noqa: E402


def main() -> int:
    date_str = "2026-07-22"
    files = bravo.locate_store_files(date_str, "fpd-cohort.csv")
    missing = bravo.missing_stores(files)
    if missing:
        print(f"FAIL: missing stores: {missing}")
        return 1

    cohorts = {s: formats.extract_fpd_cohort(p) for s, p in files.items()}
    archive = bravo.read_fpd_archive()
    got = formats.render_fpd_ranking(cohorts, date_str, archive)
    expected = (FIXTURES / "fpd_ranking_2026-07-22.txt").read_text()

    if got.strip() != expected.strip():
        import difflib
        print("FAIL — mismatch:")
        sys.stdout.writelines(difflib.unified_diff(
            expected.strip().splitlines(keepends=True), got.strip().splitlines(keepends=True),
            fromfile="expected (real post)", tofile="got",
        ))
        return 1

    print("PASS — matches the real 2026-07-22 post exactly (store ranking, this-week and chronic categories).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
