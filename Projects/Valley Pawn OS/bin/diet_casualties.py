#!/usr/bin/env python3
"""diet_casualties.py — which tasks were RUNNING SUCCESSFULLY when the 2026-09-16 diet disabled them?

WHY (Joshua, 2026-09-21): "you have been using chekkit fine for months, go back and see how and why
it was working so well and what changed." He was right to push. #google-reviews carried per-review
alerts several times a day until 2026-09-16 18:12 and then stopped dead — and
`chekkit-new-review-alert` is DISABLED with lastRunAt 2026-09-16T23:22. The fleet diet that day cut
enabled tasks 167 -> 55 and took working automations with it.

This separates the two kinds of disabled task, which matter very differently:
  RETIRED  — replaced by a native agent on purpose (pawn-walk, sold-review, ...). Correct.
  CASUALTY — was running fine right up to the diet, has no native replacement. A live automation
             switched off, and nobody has looked at the list since.

Judgement stays with Joshua: this prints the evidence, it re-enables nothing.
"""
import datetime as dt, json, os
REG = os.path.expanduser("~/Library/Application Support/Claude/local-agent-mode-sessions/"
                         "823f6874-6252-4031-ae4e-a3c22d37598e/f6b75d02-cca9-4943-ad6e-88390a3f201d/"
                         "scheduled-tasks.json")
LA = os.path.expanduser("~/Library/LaunchAgents")
DIET = dt.datetime(2026, 9, 16)
native = set()
for f in os.listdir(LA):
    if f.startswith("com.valleypawn."):
        native.add(f[len("com.valleypawn."):-len(".plist")].lower())
tasks = json.load(open(REG))["scheduledTasks"]
cas, retired, stale = [], [], []
for t in tasks:
    if t.get("enabled"):
        continue
    tid = str(t.get("id"))
    lr = t.get("lastRunAt")
    if not lr:
        continue
    try:
        d = dt.datetime.fromisoformat(str(lr)[:19])
    except ValueError:
        continue
    key = tid.lower().replace("_", "-")
    has_native = any(key in n or n in key for n in native)
    # ran within the 4 days before the diet = it was alive when switched off
    if (DIET - dt.timedelta(days=4)) <= d <= (DIET + dt.timedelta(days=2)):
        (retired if has_native else cas).append((tid, str(lr)[:16], has_native))
    elif d < DIET - dt.timedelta(days=4):
        stale.append((tid, str(lr)[:16]))
print("# What the 2026-09-16 fleet diet switched off\n")
print("## CASUALTIES — running right up to the diet, NO native replacement (%d)\n" % len(cas))
print("| Task | last successful run |")
print("|---|---|")
for tid, lr, _ in sorted(cas, key=lambda r: r[1], reverse=True):
    print("| **%s** | %s |" % (tid, lr))
print("\n## Retired on purpose — a native agent took over (%d)\n" % len(retired))
for tid, lr, _ in sorted(retired):
    print("- %s (last Cowork run %s)" % (tid, lr))
print("\n## Already stale before the diet — not casualties (%d)\n" % len(stale))
for tid, lr in sorted(stale, key=lambda r: r[1], reverse=True)[:12]:
    print("- %s (last ran %s)" % (tid, lr))
print("\nSUMMARY casualties=%d retired=%d stale=%d" % (len(cas), len(retired), len(stale)))
