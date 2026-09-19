#!/usr/bin/env python3
"""install_dryrun_check.py — teach every Tier-1 Cowork task to honour the fleet publish guard.

WHY: bin/vp_dryrun.py is ENFORCED for native scripts, because they all publish through vp_slack.py
and that is one chokepoint to check. Cowork tasks publish through the Slack connector instead —
there is no chokepoint to intercept, so for those the guard can only be an INSTRUCTION the task
follows. That distinction is real and is stated plainly in the block below rather than papered over:
native = enforced, Cowork = honoured.

Without this, "test the fleet in isolation" is impossible for the tasks that matter most — the ones
that publish to store managers and team channels, where a test run is not a test, it is a message
your staff acts on.

SAFE BY CONSTRUCTION: idempotent, additive (appends only), backs up before every write, and reports
any task whose manifest name has no Scheduled/ folder instead of inventing one.

    install_dryrun_check.py             # dry run — prints what it WOULD do
    install_dryrun_check.py --apply
"""
import datetime as dt
import json
import os
import sys

HOME = os.path.expanduser("~")
OS_DIR = os.path.join(HOME, "Documents/Claude/Projects/Valley Pawn OS")
MANIFEST = os.path.join(OS_DIR, "fleet/expected_outputs.json")
TIER1 = os.path.join(OS_DIR, "fleet/tier1_tasks.json")
SCHEDULED = os.path.join(HOME, "Documents/Claude/Scheduled")
MARK = "FLEET PUBLISH GUARD"

BLOCK = """

## Precondition (MANDATORY) — %s

Before publishing ANYTHING — a channel post, a DM to Joshua, a DM to a store manager, a canvas
refresh, an email, a Facebook post — check whether the fleet publish guard is armed:

```bash
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_dryrun.py" status
```

Exit code 0 means **ARMED**. When it is armed:

- Do the ENTIRE task for real — same pull, same data, same compile, same message text. The point is
  to test the task, not to skip it.
- Publish NOTHING. Not to a channel, not to a DM, not to a manager, not to a canvas, not anywhere.
- Instead write exactly what you would have published to
  `Valley Pawn OS/fleet/test_output/<task-name>-<YYYYMMDD-HHMMSS>.txt`, with a first line naming the
  channel or person it would have gone to.
- Do NOT write a normal publication receipt. A diverted run is not evidence that the task delivered,
  and recording it as one would corrupt the fleet audit.
- Say clearly in your final summary that the guard was armed and nothing was published.

Exit code 1 means not armed — run and publish normally.

This guard is ENFORCED for native scripts (they all publish through `vp_slack.py`, which intercepts
them). A Cowork task like this one has no such chokepoint, so here the guard is only as good as this
instruction. Honour it exactly. The guard always carries an expiry and disarms itself, so a stale
flag can never silence this task indefinitely.
""" % MARK


def main():
    apply = "--apply" in sys.argv
    tier1_doc = json.load(open(TIER1))
    tier1 = {t for g in tier1_doc.get("tier1", {}).values() for t in g}
    entries = [e for e in json.load(open(MANIFEST))["entries"] if e.get("task") in tier1]
    seen, tasks = set(), []
    for e in entries:                              # a task can hold two entries (two daily instances)
        if e["task"] not in seen:
            seen.add(e["task"])
            tasks.append(e["task"])
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    done = skipped = missing = native = 0
    for task in sorted(tasks):
        path = os.path.join(SCHEDULED, task, "SKILL.md")
        if not os.path.isfile(path):
            # native launchd agents have no Scheduled/ folder — they are already ENFORCED, not
            # instructed, so this is the expected outcome for them, not an error.
            print("native   %-40s no Scheduled/ folder — enforced via vp_slack.py" % task)
            native += 1
            continue
        body = open(path, encoding="utf-8").read()
        if MARK in body:
            print("already  %-40s guard check present" % task)
            skipped += 1
            continue
        if not apply:
            print("WOULD ADD %-39s" % task)
            done += 1
            continue
        with open(path + ".bak-dryrun-" + stamp, "w", encoding="utf-8") as f:
            f.write(body)
        with open(path, "a", encoding="utf-8") as f:
            f.write(BLOCK)
        print("ADDED    %-40s" % task)
        done += 1
    print("\n%s: %d written, %d already had it, %d native (enforced, no SKILL needed), %d total Tier-1"
          % ("APPLIED" if apply else "DRY RUN", done, skipped, native, len(tasks)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
