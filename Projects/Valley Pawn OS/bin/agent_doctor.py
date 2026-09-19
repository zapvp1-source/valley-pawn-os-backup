#!/usr/bin/env python3
"""agent_doctor.py — cross-check every launchd agent against the program it actually runs.

WHY (2026-09-18): log triage found `dashboard-data-collector` failing on EVERY fire with
"No such file or directory" — a launchd agent still scheduled, still waking up, pointing at a
script that does not exist. It had written 278 error lines and nobody knew, because a failing
agent's only output is a log nobody reads.

This is a whole CLASS of fault, not one bug: an agent whose target was moved, renamed, or deleted
looks perfectly healthy in `launchctl list` and in the task registry. The only way to catch it is to
read each plist and stat the program it points at.

Read-only. Reports; changes nothing. Unloading an agent is a deliberate act for a human or a
separate, named script — never a side effect of a diagnostic.

    agent_doctor.py
"""
import glob
import os
import plistlib
import sys

LA = os.path.expanduser("~/Library/LaunchAgents")


def program_of(d):
    """(path, argv_display). ProgramArguments[0] wins; Program is the fallback."""
    pa = d.get("ProgramArguments")
    if isinstance(pa, list) and pa:
        return pa[0], " ".join(str(x) for x in pa[:4])
    p = d.get("Program")
    if p:
        return p, str(p)
    return None, "(none declared)"


def script_arg(d):
    """The first .sh/.py argument, which is what actually has to exist for an interpreter agent."""
    pa = d.get("ProgramArguments") or []
    for a in pa[1:]:
        if isinstance(a, str) and (a.endswith(".sh") or a.endswith(".py")):
            return a
    return None


def main():
    files = sorted(glob.glob(os.path.join(LA, "*.plist")))
    if not files:
        print("no plists in %s" % LA)
        return 0
    broken, ok, unreadable = [], [], []
    for f in files:
        name = os.path.basename(f)[:-6]
        try:
            with open(f, "rb") as fh:
                d = plistlib.load(fh)
        except Exception as e:
            unreadable.append((name, str(e)[:100]))
            continue
        prog, disp = program_of(d)
        missing = []
        if prog and not os.path.exists(prog):
            missing.append("program %s" % prog)
        s = script_arg(d)
        if s and not os.path.exists(s):
            missing.append("script %s" % s)
        for key in ("StandardOutPath", "StandardErrorPath", "WorkingDirectory"):
            v = d.get(key)
            if key == "WorkingDirectory" and v and not os.path.isdir(v):
                missing.append("workdir %s" % v)
        if missing:
            broken.append((name, disp, missing, d))
        else:
            ok.append((name, disp))
    print("# launchd agent doctor — %d agents\n" % len(files))
    if broken:
        print("## BROKEN (%d) — scheduled, waking up, and failing every single fire\n" % len(broken))
        print("| Agent | Missing | Runs |")
        print("|---|---|---|")
        for name, disp, missing, d in broken:
            sched = "KeepAlive" if d.get("KeepAlive") else (
                "every %ss" % d["StartInterval"] if d.get("StartInterval") else
                ("%d time(s)/day" % len(d["StartCalendarInterval"]) if isinstance(d.get("StartCalendarInterval"), list)
                 else ("daily" if d.get("StartCalendarInterval") else "?")))
            print("| %s | %s | %s |" % (name, "; ".join(missing)[:110], sched))
        print("\nEach of these is either a job that must be restored, or an agent that must be")
        print("unloaded. Leaving it is the worst of both: it costs wakeups, fills logs with noise,")
        print("and makes a real failure harder to see. This tool does not unload anything.")
    if unreadable:
        print("\n## UNREADABLE (%d)\n" % len(unreadable))
        for name, err in unreadable:
            print("- **%s** — %s" % (name, err))
    print("\n## HEALTHY (%d) — program and script both present\n" % len(ok))
    for name, disp in ok:
        print("- %s" % name)
    # Stable contract line for fleet_doctor.sh (see log_triage.py for why prose-grepping failed).
    # Only OUR agents count: a broken third-party agent is not Valley Pawn's to fix or to alarm on.
    mine = [n for n, _, _, _ in broken if n.startswith("com.valleypawn.")]
    print("\nSUMMARY broken_vp=%d broken_other=%d healthy=%d unreadable=%d"
          % (len(mine), len(broken) - len(mine), len(ok), len(unreadable)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
