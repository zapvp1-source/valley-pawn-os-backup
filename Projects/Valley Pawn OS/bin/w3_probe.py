#!/usr/bin/env python3
"""w3_probe.py — READ-ONLY probes for the Mac-first wave 3 (monthlies) builds (2026-10-19). Never writes or posts.
  w3_probe.py agents            launchctl rows for every com.valleypawn.* agent (loaded / last exit)
  w3_probe.py drive             which Drive-for-Desktop folders the monthlies write to actually exist
  w3_probe.py google            scopes the Google refresh token really holds (Website/analytics/bin/google_auth)
  w3_probe.py live              which fleet/state/native_live/<task> files exist
"""
import glob
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OS_DIR = os.path.dirname(HERE)
PROJ = os.path.dirname(OS_DIR)
CLOUD = os.path.expanduser("~/Library/CloudStorage")


def agents():
    r = subprocess.run(["launchctl", "list"], capture_output=True, text=True)
    rows = [l for l in r.stdout.splitlines() if "com.valleypawn." in l]
    for l in sorted(rows, key=lambda x: x.split("\t")[-1]):
        print(l)
    print("%d com.valleypawn agents loaded" % len(rows))


def drive():
    for root in sorted(glob.glob(os.path.join(CLOUD, "GoogleDrive-*"))):
        print("root:", root)
        for sub in ("Shared drives", "My Drive"):
            p = os.path.join(root, sub)
            print("  %s: %s" % (sub, "exists" if os.path.isdir(p) else "MISSING"))
        for cand in ("Shared drives/Valley Pawn Drive/Accounting Exports", "Shared drives/Valley Pawn Drive/Trends",
                     "My Drive/01 Business/Full Circle Finance (Valley Pawn)/08 Reports & Analysis/Gift Card & Store Credit",
                     "My Drive/00 Inbox/Desktop Spreadsheets Import (Needs Sorting)/VP BONUS FINAL Updated.xlsx"):
            p = os.path.join(root, cand)
            print("  %s -> %s" % (cand, "OK" if os.path.exists(p) else "MISSING"))
        sys.path.insert(0, HERE)
        import eom_gl_export
        print("  Accounting Exports found at:", eom_gl_export.drive_folder() or "nowhere (depth <= 6 under My Drive / Shared drives)")


def google():
    sys.path.insert(0, os.path.join(PROJ, "Website", "analytics", "bin"))
    import google_auth
    print("scopes:", google_auth.scopes())


def live():
    d = os.path.join(OS_DIR, "fleet", "state", "native_live")
    print("\n".join(sorted(os.listdir(d))) if os.path.isdir(d) else "no native_live dir")


if __name__ == "__main__":
    {"agents": agents, "drive": drive, "google": google, "live": live}.get(sys.argv[1] if len(sys.argv) > 1 else "", lambda: print(__doc__))()
