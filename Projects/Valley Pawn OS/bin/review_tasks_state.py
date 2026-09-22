#!/usr/bin/env python3
"""review_tasks_state.py — which review/Chekkit tasks exist, and are they still enabled?

WHY (2026-09-21): #google-reviews carried per-review alerts ("Nice job Team X! ... 5 star review")
several times a DAY through 2026-09-16 18:12, then stopped dead. The weekly ranked summary posted
cleanly at 09:00 on 08/31 and 09/07. So Chekkit access was healthy until 9/16 — the same day the
fleet diet cut enabled tasks from 167 to 55. The obvious question nobody has asked: did the diet
disable automations that were WORKING?
"""
import json, os, re
REG = os.path.expanduser("~/Library/Application Support/Claude/local-agent-mode-sessions/"
                         "823f6874-6252-4031-ae4e-a3c22d37598e/f6b75d02-cca9-4943-ad6e-88390a3f201d/"
                         "scheduled-tasks.json")
SCHED = os.path.expanduser("~/Documents/Claude/Scheduled")
d = json.load(open(REG))
tasks = d["scheduledTasks"]
skips = d.get("recordedSkips") or {}
PAT = re.compile(r"chekkit|google[- ]review|review invitation|nice job team|5 star", re.I)
rows = []
for t in tasks:
    tid = str(t.get("id"))
    p = os.path.join(SCHED, tid, "SKILL.md")
    hit = PAT.search(tid) is not None
    if not hit and os.path.isfile(p):
        try:
            hit = bool(PAT.search(open(p, errors="replace").read()[:20000]))
        except OSError:
            pass
    if hit:
        rows.append((tid, bool(t.get("enabled")), t.get("lastRunAt"), t.get("chromePermissionMode")))
print("# Review / Chekkit related tasks\n")
print("| Task | enabled | lastRunAt | permMode |")
print("|---|---|---|---|")
for tid, en, lr, pm in sorted(rows, key=lambda r: (r[1], r[0])):
    print("| %s | %s | %s | %s |" % (tid, "YES" if en else "**NO**", (lr or "never")[:19], pm))
off = [r[0] for r in rows if not r[1]]
print("\n**%d of %d are DISABLED:** %s" % (len(off), len(rows), ", ".join(off) or "none"))
print("\n## recordedSkips mentioning these tasks\n")
n = 0
for k, v in list(skips.items()):
    if any(t in str(k) for t, _, _, _ in rows):
        print("- %s -> %s" % (k, str(v)[:160])); n += 1
        if n > 12: break
if n == 0:
    print("(none)")
