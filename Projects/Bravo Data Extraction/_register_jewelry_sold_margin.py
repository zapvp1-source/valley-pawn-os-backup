#!/usr/bin/env python3
"""Additively register the NEW 'jewelry-margin-sold' cell. ADD-only, idempotent, backs up."""
import shutil, sys, time
from pathlib import Path

BASE = Path("/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction")
STAMP = time.strftime("%Y-%m-%dT%H%M%S")
NEW_INCLUDE = r"#Include reports\JewelrySoldMargin.ahk"
ANCHOR_INCLUDE = r"#Include reports\AgedJewelrySales.ahk"
NEW_CELL_KEY = 'REPORT_HANDLERS["jewelry-margin-sold"]'
ANCHOR_CELL_KEY = 'REPORT_HANDLERS["aged-jewelry-sales"]'
NEW_CELL_FN = "PullJewelrySoldMargin"

ok = True
for fname in ["bravo_watcher.ahk", "bravo_export.ahk"]:
    path = BASE / fname
    text = path.read_text(encoding="utf-8", errors="surrogateescape")
    lines = text.splitlines(keepends=True)
    changed = False

    if NEW_INCLUDE not in text:
        done = False
        for i, ln in enumerate(lines):
            if ln.strip() == ANCHOR_INCLUDE.strip():
                nl = "\r\n" if ln.endswith("\r\n") else "\n"
                lines.insert(i + 1, NEW_INCLUDE + nl); done = changed = True; break
        if not done:
            for i in range(len(lines) - 1, -1, -1):
                if lines[i].strip().startswith("#Include reports"):
                    nl = "\r\n" if lines[i].endswith("\r\n") else "\n"
                    lines.insert(i + 1, NEW_INCLUDE + nl); changed = True; break

    if NEW_CELL_KEY not in "".join(lines):
        for i, ln in enumerate(lines):
            if ANCHOR_CELL_KEY in ln and ":=" in ln:
                indent = ln[: len(ln) - len(ln.lstrip())]
                nl = "\r\n" if ln.endswith("\r\n") else "\n"
                lines.insert(i + 1, f"{indent}{NEW_CELL_KEY} := {NEW_CELL_FN}{nl}")
                changed = True; break

    if changed:
        shutil.copy2(path, path.with_suffix(path.suffix + f".bak-pre-jewelry-margin-{STAMP}"))
        path.write_text("".join(lines), encoding="utf-8", errors="surrogateescape")

    t = path.read_text(encoding="utf-8", errors="surrogateescape")
    has_inc, has_cell = NEW_INCLUDE in t, NEW_CELL_KEY in t
    print(f"{fname}: include={has_inc} dispatch={has_cell}")
    ok = ok and has_inc and has_cell

print(f"handler exists: {(BASE/'reports'/'JewelrySoldMargin.ahk').exists()}")
sys.exit(0 if ok else 1)
