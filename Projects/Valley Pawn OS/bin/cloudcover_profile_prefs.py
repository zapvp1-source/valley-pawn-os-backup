#!/usr/bin/env python3
"""cloudcover_profile_prefs.py — make the CloudCover automation Chrome profile keep its sign-in across restarts
(session.restore_on_startup = 1 'Continue where you left off', which persists session cookies). 2026-10-16.
Run only while that profile's Chrome is closed."""
import json, os, shutil, subprocess, sys
P = os.path.expanduser("~/Library/Application Support/valleypawn/pw-cloudcover/Default/Preferences")
if subprocess.run(["pgrep", "-f", "--user-data-dir=" + os.path.dirname(os.path.dirname(P))], capture_output=True).stdout.strip():
    print("automation Chrome is open — close it first"); sys.exit(2)
d = json.load(open(P)) if os.path.exists(P) else {}
shutil.copy(P, P + ".bak-20261016") if os.path.exists(P) else None
d.setdefault("session", {})["restore_on_startup"] = 1
d.setdefault("profile", {})["exit_type"] = "Normal"
json.dump(d, open(P, "w"))
print("restore_on_startup =", d["session"]["restore_on_startup"])
