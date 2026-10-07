#!/usr/bin/env python3
"""quiet_triage.py [log names...] — READ-ONLY: map every valleypawn launchd agent to its schedule,
logs, loaded state and last exit; list logs no plist claims; tail the named logs.

WHY (2026-10-06): fleet-doctor reported 20 "quiet" logs. Deciding whether each is dead, retired or
just mis-measured needs plist + launchctl + log tails together, and the sandbox cannot see
~/Library. Nothing here changes state.
"""
import datetime as dt, glob, os, plistlib, subprocess, sys

LA = os.path.expanduser("~/Library/LaunchAgents")
LOG = os.path.expanduser("~/Library/Logs/valleypawn")
now = dt.datetime.now()

loaded = {}
try:
    out = subprocess.run(["launchctl", "list"], capture_output=True, text=True).stdout
    for l in out.splitlines()[1:]:
        p = l.split("\t")
        if len(p) == 3 and "valleypawn" in p[2]:
            loaded[p[2]] = (p[0], p[1])
except Exception as e:
    print("launchctl list failed:", e)

claimed = set()
print("# agents (label | loaded pid/lastexit | schedule | target exists | logs)")
for f in sorted(glob.glob(os.path.join(LA, "*valleypawn*.plist"))):
    try:
        d = plistlib.load(open(f, "rb"))
    except Exception as e:
        print("UNREADABLE", f, e); continue
    lab = d.get("Label", os.path.basename(f))
    pa = d.get("ProgramArguments") or [d.get("Program", "")]
    tgt = pa[1] if len(pa) > 1 else pa[0]
    sched = d.get("StartCalendarInterval") or ("every %ss" % d["StartInterval"] if d.get("StartInterval") else "")
    if d.get("RunAtLoad"): sched = "%s RunAtLoad" % sched
    if d.get("KeepAlive"): sched = "%s KeepAlive" % sched
    logs = []
    for k in ("StandardOutPath", "StandardErrorPath"):
        v = d.get(k)
        if v:
            claimed.add(os.path.basename(v))
            logs.append(os.path.basename(v))
    print("%s | %s | %s | %s %s | %s" % (lab, loaded.get(lab, "NOT LOADED"), sched,
          "OK" if os.path.exists(tgt) else "MISSING", " ".join(pa[1:4]), " ".join(logs)))

print("\n# loaded but no plist file")
for lab in sorted(loaded):
    if not os.path.exists(os.path.join(LA, lab + ".plist")):
        print(lab, loaded[lab])

print("\n# logs not named by any plist (age h)")
for p in sorted(glob.glob(os.path.join(LOG, "*.log"))):
    b = os.path.basename(p)
    if b not in claimed:
        print("%s %.0fh" % (b, (now - dt.datetime.fromtimestamp(os.path.getmtime(p))).total_seconds() / 3600))

for name in [a for a in sys.argv[1:] if a.endswith(".log")]:
    p = os.path.join(LOG, os.path.basename(name))
    print("\n== %s ==" % name)
    if not os.path.isfile(p):
        print("  (absent)"); continue
    print("  mtime %s size %d" % (dt.datetime.fromtimestamp(os.path.getmtime(p)).strftime("%m/%d %H:%M"), os.path.getsize(p)))
    for l in open(p, errors="replace").read().splitlines()[-6:]:
        print("  " + l[:220])


# --grep-agents <text>: which LaunchAgents (any label) mention <text>; --grep-file <path> <regex>: matching lines
# of one file (read-only). Added 2026-10-06 to find a second runner of the Oura importer.
if "--grep-agents" in sys.argv:
    t = sys.argv[sys.argv.index("--grep-agents") + 1]
    print("\n# LaunchAgents mentioning %r" % t)
    for f in sorted(glob.glob(os.path.join(LA, "*.plist"))):
        try:
            raw = open(f, "rb").read()
            if t.encode() in raw:
                d = plistlib.loads(raw)
                print(os.path.basename(f), d.get("StartCalendarInterval") or d.get("StartInterval"), d.get("ProgramArguments"))
        except Exception as e:
            print("unreadable", f, e)
if "--grep-file" in sys.argv:
    import re
    i = sys.argv.index("--grep-file")
    path, rx = os.path.expanduser(sys.argv[i + 1]), re.compile(sys.argv[i + 2])
    print("\n# %s matching %s" % (path, rx.pattern))
    for n, l in enumerate(open(path, errors="replace"), 1):
        if rx.search(l):
            print("%4d %s" % (n, l.rstrip()[:200]))
