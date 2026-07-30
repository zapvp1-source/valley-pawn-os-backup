#!/usr/bin/env python3
"""
Additively register the NEW 'jewelry-count-audit' pipeline cell (Jewelry
Count Reconciliation project, 2026-07-29).

DO NOT RUN while Bravo/the watcher is mid-job. Check for live activity
first: `ls -lt output/*.csv | head` and `ls -lt triggers/claimed | head` —
if timestamps are within the last few minutes, wait.

valley-pawn-context Rule #4: ADD lines only. Idempotent -- running it twice
changes nothing the second time. Backs up each touched file with a
timestamped .bak before writing.
"""
import shutil
import sys
import time
from pathlib import Path

BASE = Path(".")
STAMP = time.strftime("%Y-%m-%dT%H%M%S")

NEW_INCLUDE = r"#Include reports\JewelryCountAudit.ahk"
ANCHOR_INCLUDE = r"#Include reports\JewelrySoldMargin.ahk"

NEW_CELL_KEY = 'REPORT_HANDLERS["jewelry-count-audit"]'
ANCHOR_CELL_KEY = 'REPORT_HANDLERS["jewelry-margin-sold"]'
NEW_CELL_FN = "PullJewelryCountAudit"

targets = ["bravo_watcher.ahk", "bravo_export.ahk"]
report = []

for fname in targets:
    path = BASE / fname
    if not path.exists():
        report.append(f"SKIP {fname}: not found")
        continue

    text = path.read_text(encoding="utf-8", errors="surrogateescape")
    lines = text.splitlines(keepends=True)

    did_include = False
    did_cell = False

    if NEW_INCLUDE in text:
        report.append(f"  {fname}: #Include already present (idempotent no-op)")
    else:
        for i, ln in enumerate(lines):
            if ln.strip() == ANCHOR_INCLUDE.strip():
                nl = "\r\n" if ln.endswith("\r\n") else "\n"
                lines.insert(i + 1, NEW_INCLUDE + nl)
                did_include = True
                report.append(f"  {fname}: inserted #Include after line {i+1}")
                break
        if not did_include:
            for i in range(len(lines) - 1, -1, -1):
                if lines[i].strip().startswith("#Include reports"):
                    nl = "\r\n" if lines[i].endswith("\r\n") else "\n"
                    lines.insert(i + 1, NEW_INCLUDE + nl)
                    did_include = True
                    report.append(f"  {fname}: inserted #Include after last include (line {i+1})")
                    break
        if not did_include:
            report.append(f"  {fname}: !! could not find an #Include anchor")

    if NEW_CELL_KEY in "".join(lines):
        report.append(f"  {fname}: dispatch entry already present (idempotent no-op)")
    else:
        for i, ln in enumerate(lines):
            if ANCHOR_CELL_KEY in ln and ":=" in ln:
                indent = ln[: len(ln) - len(ln.lstrip())]
                nl = "\r\n" if ln.endswith("\r\n") else "\n"
                anchor_col = ln.index(":=") - len(indent)
                key = NEW_CELL_KEY
                pad = max(1, anchor_col - len(key))
                new_line = f"{indent}{key}{' ' * pad}:= {NEW_CELL_FN}{nl}"
                lines.insert(i + 1, new_line)
                did_cell = True
                report.append(f"  {fname}: inserted dispatch entry after line {i+1}")
                break
        if not did_cell:
            report.append(f"  {fname}: !! could not find a dispatch anchor")

    if did_include or did_cell:
        bak = path.with_suffix(path.suffix + f".bak-pre-jewelry-count-audit-{STAMP}")
        shutil.copy2(path, bak)
        path.write_text("".join(lines), encoding="utf-8", errors="surrogateescape")
        report.append(f"  {fname}: WROTE (backup -> {bak.name})")

print("\n".join(report))

print("\n--- VERIFY ---")
ok = True
for fname in targets:
    path = BASE / fname
    if not path.exists():
        continue
    t = path.read_text(encoding="utf-8", errors="surrogateescape")
    has_inc = NEW_INCLUDE in t
    has_cell = NEW_CELL_KEY in t
    print(f"{fname}: include={has_inc} dispatch={has_cell}")
    if not (has_inc and has_cell):
        ok = False

handler = BASE / "reports" / "JewelryCountAudit.ahk"
print(f"handler file exists: {handler.exists()} ({handler.stat().st_size if handler.exists() else 0} bytes)")

sys.exit(0 if ok else 1)
