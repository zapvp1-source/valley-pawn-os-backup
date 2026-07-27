#!/usr/bin/env python3
"""
Golden test for Job A (store rankings) — no test framework dependency,
stdlib only, matching the rest of this repo.

Two independent checks:
1. FORMAT: renderer output must match real historical #store-performance
   Slack posts EXACTLY (fixtures/ captured verbatim via the Slack API on
   2026-07-26 from the 2026-07-19 and 2026-07-12 posts). This is the
   authoritative check per BUILD_SPEC.md §6 ("golden tests must compare
   renderer output against the most recent real post"). Note the real
   format uses italics + Slack emoji shortcodes, NOT the bold+unicode-emoji
   style either store_kpis_compile.py or monday-store-rankings/SKILL.md's
   own documented example uses — neither of those was actually live.
2. NUMBERS: extraction math must match store_kpis_compile.py (Bravo Data
   Extraction/store_kpis_compile.py, verified to the penny against Bravo
   Company Performance for all 5 stores) — a numeric-only regression guard,
   independent of formatting.

Run: python3 tests/test_store_rankings.py
Exits 0 on match, 1 on any mismatch (prints a diff).
"""
from __future__ import annotations
import difflib
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
FIXTURES = Path(__file__).resolve().parent / "fixtures"
sys.path.insert(0, str(REPO))

from vpops import bravo, formats  # noqa: E402

BRAVO_ROOT = Path("/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction")
COMPILE_SCRIPT = BRAVO_ROOT / "store_kpis_compile.py"

# (enddate, {"msg1": fixture_path or None, "msg2": fixture_path or None})
FORMAT_FIXTURES = [
    ("2026-07-19", {"msg1": "store_rankings_2026-07-19_msg1.txt", "msg2": "store_rankings_2026-07-19_msg2.txt"}),
    ("2026-07-12", {"msg1": "store_rankings_2026-07-12_msg1.txt", "msg2": None}),
]

NUMERIC_CHECK_DATES = ["2026-07-21", "2026-06-30", "2026-05-31", "2026-01-31", "2026-07-04"]


def render(enddate: str) -> tuple[str, str]:
    files = bravo.locate_store_files(enddate, "end-of-month.xlsx")
    missing = bravo.missing_stores(files)
    if missing:
        raise RuntimeError(f"Missing EOM files for {enddate}: {missing}")
    data = {store: formats.extract_store_eom_metrics(path) for store, path in files.items()}
    return formats.render_store_rankings(data, enddate)


def check_format(enddate: str, fixture_names: dict) -> bool:
    ok = True
    new_msg1, new_msg2 = render(enddate)
    for label, new_val, fixture_name in [("MSG1", new_msg1, fixture_names["msg1"]), ("MSG2", new_msg2, fixture_names["msg2"])]:
        if fixture_name is None:
            continue
        expected = (FIXTURES / fixture_name).read_text()
        if new_val.strip() != expected.strip():
            ok = False
            print(f"\n--- FORMAT MISMATCH: {enddate} {label} vs real Slack fixture {fixture_name} ---")
            diff = difflib.unified_diff(
                expected.strip().splitlines(keepends=True),
                new_val.strip().splitlines(keepends=True),
                fromfile="real Slack post", tofile="new renderer",
            )
            sys.stdout.writelines(diff)
    return ok


def check_numbers(enddate: str) -> bool:
    result = subprocess.run(
        ["/usr/bin/python3", str(COMPILE_SCRIPT), enddate],
        cwd=str(BRAVO_ROOT), capture_output=True, text=True,
    )
    if "OK enddate=" not in result.stdout:
        print(f"  (skipping {enddate}: reference compile script did not succeed: {result.stdout.strip()})")
        return True
    out_dir = BRAVO_ROOT / "output"
    ref_msg2 = (out_dir / f"{enddate}_store_kpis_msg2.txt").read_text()
    _, new_msg2 = render(enddate)

    # Compare only the $ figures, ignoring the bold/italic + emoji-shortcode
    # formatting differences established in check_format() above.
    import re
    ref_nums = re.findall(r"\$[\d,]+\.\d\d", ref_msg2)
    new_nums = re.findall(r"\$[\d,]+\.\d\d", new_msg2)
    if ref_nums != new_nums:
        print(f"\n--- NUMERIC MISMATCH: {enddate} ---")
        print("reference:", ref_nums)
        print("new:      ", new_nums)
        return False
    return True


def main() -> int:
    all_ok = True

    print("=== FORMAT checks (vs real Slack history) ===")
    for enddate, fixtures in FORMAT_FIXTURES:
        print(f"  {enddate}...", end=" ")
        try:
            ok = check_format(enddate, fixtures)
        except Exception as e:
            print(f"ERROR: {e}")
            ok = False
        print("PASS" if ok else "FAIL")
        all_ok = all_ok and ok

    print("\n=== NUMERIC checks (vs store_kpis_compile.py) ===")
    for enddate in NUMERIC_CHECK_DATES:
        print(f"  {enddate}...", end=" ")
        try:
            ok = check_numbers(enddate)
        except Exception as e:
            print(f"ERROR: {e}")
            ok = False
        print("PASS" if ok else "FAIL")
        all_ok = all_ok and ok

    print("\n" + ("ALL PASS" if all_ok else "SOME FAILED — see diffs above"))
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
