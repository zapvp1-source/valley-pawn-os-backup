#!/usr/bin/env python3
"""Fleet diet — Phase 0.3 of FLEET_DEEP_DIVE_2026-09-16.md (Joshua approved 2026-09-16).

Run ONLY while Claude.app is fully quit (bin/fleet_diet_apply.sh handles quiesce/relaunch),
and ONLY against a registry that holds the full fleet (>= MIN_TASKS). Refuses otherwise.

What it does (additive, reversible):
  * every ENABLED task whose id is NOT in fleet/tier1_tasks.json -> enabled = false
  * tasks already disabled are untouched; Tier-1 tasks are untouched
  * prior enabled-state of EVERY task saved to fleet/fleet_diet_rollback.json (run once; never overwritten)
  * registry backed up to <registry>.bak-diet-<stamp>; atomic write; JSON reload check
  * NEVER writes null (the 9/10 outage class) — verified before write

Rollback: python3 bin/fleet_diet_registry_edit.py --rollback   (app quit first)
Dry run:  python3 bin/fleet_diet_registry_edit.py --dry-run
"""
import glob, json, os, shutil, sys, time

HOME = os.path.expanduser("~")
OS_DIR = os.path.join(HOME, "Documents/Claude/Projects/Valley Pawn OS")
TIER1 = os.path.join(OS_DIR, "fleet/tier1_tasks.json")
ROLLBACK = os.path.join(OS_DIR, "fleet/fleet_diet_rollback.json")
REGGLOB = os.path.join(HOME, "Library/Application Support/Claude/local-agent-mode-sessions/*/*/scheduled-tasks.json")
MIN_TASKS = 150
DRY = "--dry-run" in sys.argv
ROLL = "--rollback" in sys.argv
STAMP = time.strftime("%Y%m%d-%H%M%S")


def find_registry():
    files = sorted(glob.glob(REGGLOB), key=os.path.getmtime, reverse=True)
    if not files:
        sys.exit("ABORT: no registry file found")
    return files[0]


def has_null(obj):
    if obj is None:
        return True
    if isinstance(obj, dict):
        return any(has_null(v) for v in obj.values())
    if isinstance(obj, list):
        return any(has_null(v) for v in obj)
    return False


def atomic_write(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2)
    json.load(open(tmp))  # reload check
    os.replace(tmp, path)


def main():
    reg = find_registry()
    d = json.load(open(reg))
    tasks = d.get("scheduledTasks", [])
    print("registry:", reg, "tasks:", len(tasks), "enabled:", sum(1 for t in tasks if t.get("enabled")))
    if len(tasks) < MIN_TASKS:
        sys.exit("ABORT: registry holds %d tasks (< %d) — refusing to edit a partial/empty registry" % (len(tasks), MIN_TASKS))

    if ROLL:
        prior = json.load(open(ROLLBACK))["enabled_before"]
        changed = []
        for t in tasks:
            if t["id"] in prior and bool(t.get("enabled")) != prior[t["id"]]:
                t["enabled"] = prior[t["id"]]; changed.append(t["id"])
        print("rollback would restore", len(changed), "tasks:", changed)
    else:
        tier1 = json.load(open(TIER1))["tier1"]
        keep = {tid for group in tier1.values() for tid in group}
        missing = sorted(keep - {t["id"] for t in tasks})
        if missing:
            print("WARNING: Tier-1 ids not in registry:", missing)
        if not os.path.exists(ROLLBACK):
            snap = {"_created": STAMP, "enabled_before": {t["id"]: bool(t.get("enabled")) for t in tasks}}
            if not DRY:
                atomic_write(ROLLBACK, snap)
            print("rollback snapshot", "(dry)" if DRY else "written", ROLLBACK)
        changed = []
        for t in tasks:
            if t.get("enabled") and t["id"] not in keep:
                t["enabled"] = False; changed.append(t["id"])
        print("parking", len(changed), "tasks; Tier-1 staying enabled:",
              sum(1 for t in tasks if t.get("enabled")))
        print(sorted(changed))

    if has_null(d):
        sys.exit("ABORT: null present in registry data — would recreate the 9/10 outage; not writing")
    if DRY:
        print("DRY RUN — nothing written"); return
    bak = reg + ".bak-diet-" + STAMP
    shutil.copy2(reg, bak); print("backup:", bak)
    atomic_write(reg, d)
    d2 = json.load(open(reg)); print("post-write tasks:", len(d2["scheduledTasks"]),
                                     "enabled:", sum(1 for t in d2["scheduledTasks"] if t.get("enabled")))


if __name__ == "__main__":
    main()
