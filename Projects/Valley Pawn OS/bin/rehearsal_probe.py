#!/usr/bin/env python3
"""rehearsal_probe.py — READ-ONLY host facts for the Nov 1 monthly rehearsal (2026-10-21). Changes nothing.

  1 does eom_gl_export.drive_folder() find the Drive-for-Desktop "Accounting Exports" folder on this Mac?
    (if not, the 11/2 GL watchdog will DM "the combined file is not in the shared-drive folder")
  2 age of the roster files the monthlies gate on (hr/ROSTER.json, fleet/state/clockin/roster.json)
  3 Bravo contention right now: _bravo_foreground_guard.sh check (read-only verb) + claimed triggers
  4 publish guard status (bin/vp_dryrun.py status)
"""
import datetime as dt
import glob
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OS_DIR = os.path.dirname(HERE)
BRAVO = os.path.join(os.path.dirname(OS_DIR), "Bravo Data Extraction")
sys.path.insert(0, HERE)

print("=== 1 Accounting Exports folder ===")
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location("eom_gl_export", os.path.join(HERE, "eom_gl_export.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    print("drive_folder():", m.drive_folder())
    print("GoogleDrive roots:", [os.path.basename(p) for p in glob.glob(os.path.join(m.CLOUD, "GoogleDrive-*"))])
except Exception as e:   # noqa: BLE001
    print("probe error:", type(e).__name__, e)

print("=== 2 roster ages ===")
for p in ("hr/ROSTER.json", "fleet/state/clockin/roster.json"):
    f = os.path.join(OS_DIR, p)
    try:
        d = json.load(open(f))
        print(p, "mtime", dt.datetime.fromtimestamp(os.path.getmtime(f)).isoformat(timespec="minutes"),
              "generated", d.get("generated_at") or d.get("generated") or d.get("as_of"))
    except Exception as e:   # noqa: BLE001
        print(p, "unreadable:", e)

print("=== 3 Bravo contention ===")
g = os.path.join(BRAVO, "_bravo_foreground_guard.sh")
if os.path.exists(g):
    r = subprocess.run(["/bin/bash", g, "check"], capture_output=True, text=True, timeout=60)
    print("foreground guard:", (r.stdout or r.stderr).strip(), "rc", r.returncode)
print("claimed triggers:", [os.path.basename(p) for p in glob.glob(os.path.join(BRAVO, "triggers", "claimed", "*.json"))][-5:])
print("queued triggers:", [os.path.basename(p) for p in glob.glob(os.path.join(BRAVO, "triggers", "*.json"))])

print("=== 4 publish guard ===")
r = subprocess.run([sys.executable, os.path.join(HERE, "vp_dryrun.py"), "status"], capture_output=True, text=True, timeout=30)
print(r.stdout.strip()[:400], "rc", r.returncode)
