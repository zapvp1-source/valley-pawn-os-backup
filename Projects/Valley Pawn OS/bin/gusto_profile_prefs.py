#!/usr/bin/env python3
"""gusto_profile_prefs.py — make the Gusto automation Chrome profile keep its sign-in across restarts
(session.restore_on_startup = 1 'Continue where you left off', which persists session cookies). 2026-10-18,
copy of cloudcover_profile_prefs.py. Run only while that profile's Chrome is closed; harmless if the profile
has no Preferences yet."""
import json, os, shutil, subprocess, sys
P = os.path.expanduser("~/Library/Application Support/valleypawn/pw-gusto/Default/Preferences")
if subprocess.run(["pgrep", "-f", "--user-data-dir=" + os.path.dirname(os.path.dirname(P))], capture_output=True).stdout.strip():
    print("automation Chrome is open — close it first"); sys.exit(2)
if not os.path.exists(P):
    print("no Preferences yet (profile never opened) — nothing to set"); sys.exit(0)
d = json.load(open(P))
shutil.copy(P, P + ".bak-20261018")
d.setdefault("session", {})["restore_on_startup"] = 1
d.setdefault("profile", {})["exit_type"] = "Normal"
json.dump(d, open(P, "w"))
print("restore_on_startup =", d["session"]["restore_on_startup"])
