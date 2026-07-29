#!/usr/bin/env python3
"""2026.6.0.79 Ok-fix: replace bare Send Enter (generator run) with Ok-click-first.

Applies to the five handlers sharing the identical pattern. Backs up each file.
Idempotent: skips files already containing the fix marker.
"""
import shutil, sys, time
from pathlib import Path

BASE = Path("/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/reports")
STAMP = time.strftime("%Y-%m-%dT%H%M%S")
MARKER = "[ok-fix 2026.6]"

OLD = '''        Sleep(2500)
        ActivateBravo()
        Sleep(500)
        Send("{Enter}")
        LogMessage("    sent {Enter}")'''

NEW = '''        Sleep(2500)
        ActivateBravo()
        Sleep(500)
        ; 2026.6.0.79 fix: Enter no longer reliably fires the generator's Ok.
        okClicked := false
        try {
            ClickByName("Ok", 5000)
            okClicked := true
            LogMessage("    [ok-fix 2026.6] clicked Ok by name")
        } catch as okErr {
            Send("{Enter}")
            LogMessage("    [ok-fix 2026.6] Ok not found (" . okErr.Message . ") -- sent {Enter} fallback")
        }'''

FILES = ["SoldInvDetails.ahk", "ActiveInvDetails.ahk", "LowDollarLoans.ahk",
         "LowDollarBuys.ahk", "LoanReviews.ahk"]

ok = True
for name in FILES:
    p = BASE / name
    text = p.read_text(encoding="utf-8", errors="surrogateescape")
    if MARKER in text:
        print(f"{name}: already patched (skip)")
        continue
    # normalize line endings for match, patch on whichever style the file uses
    if OLD in text:
        newtext = text.replace(OLD, NEW, 1)
    elif OLD.replace("\n", "\r\n") in text:
        newtext = text.replace(OLD.replace("\n", "\r\n"), NEW.replace("\n", "\r\n"), 1)
    else:
        print(f"{name}: !! pattern not found -- NOT patched")
        ok = False
        continue
    shutil.copy2(p, p.with_suffix(p.suffix + f".bak-pre-okfix-{STAMP}"))
    p.write_text(newtext, encoding="utf-8", errors="surrogateescape")
    print(f"{name}: PATCHED (backup .bak-pre-okfix-{STAMP})")

# verify
print("\n--- verify ---")
for name in FILES:
    t = (BASE / name).read_text(encoding="utf-8", errors="surrogateescape")
    print(f"{name}: marker={'yes' if MARKER in t else 'NO'}")
sys.exit(0 if ok else 1)
