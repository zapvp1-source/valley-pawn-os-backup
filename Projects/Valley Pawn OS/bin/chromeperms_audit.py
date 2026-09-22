#!/usr/bin/env python3
"""chromeperms_audit.py — which browser-driving tasks stall on a permission card unattended?

WHY (2026-09-21): review-obtained-last-week stated its own failure plainly — "no live user present
to approve site access" at 03:27. Not Chekkit (the leaderboard loads instantly when tested). It is
the permission card that `chromePermissionMode = "skip_all_permission_checks"` exists to bypass,
applied to 27 tasks on 2026-09-09 — a list this task was never on.

CORRECTED: the first version reported "enabled tasks scanned: 0", which was a parser bug, not a
clean fleet — the registry's key is `scheduledTasks` (a list) and records are keyed `id`, not
`taskId`. A zero from a tool is a tool failure until proven otherwise.

Read-only. Also reports chromeAllowedDomains, since a task can carry the skip flag and still be
blocked if the site it needs was never allow-listed.
"""
import json, os, re
REG = os.path.expanduser("~/Library/Application Support/Claude/local-agent-mode-sessions/"
                         "823f6874-6252-4031-ae4e-a3c22d37598e/f6b75d02-cca9-4943-ad6e-88390a3f201d/"
                         "scheduled-tasks.json")
SCHED = os.path.expanduser("~/Documents/Claude/Scheduled")
BROWSER = re.compile(r"claude-in-chrome|Claude_Browser|dashboard\.chekkit|navigate|get_page_text|"
                     r"browser_batch|chrome extension|read_page", re.I)
tasks = json.load(open(REG))["scheduledTasks"]
need, have, total = [], [], 0
for t in tasks:
    if not t.get("enabled"):
        continue
    total += 1
    tid = t.get("id")
    p = os.path.join(SCHED, str(tid), "SKILL.md")
    if not os.path.isfile(p):
        continue
    try:
        body = open(p, errors="replace").read()
    except OSError:
        continue
    if not BROWSER.search(body):
        continue
    row = (tid, t.get("chromePermissionMode"), t.get("chromeAllowedDomains") or [])
    (have if t.get("chromePermissionMode") == "skip_all_permission_checks" else need).append(row)
print("# Browser-driving enabled tasks — permission readiness\n")
print("enabled tasks scanned: %d · browser-driving: %d\n" % (total, len(have) + len(need)))
print("## MISSING the skip flag — these stall on a permission card unattended (%d)\n" % len(need))
for tid, m, dom in sorted(need):
    print("- **%s** — mode=%r, allowed_domains=%s" % (tid, m, dom or "none"))
print("\n## HAVE the skip flag (%d)\n" % len(have))
for tid, m, dom in sorted(have):
    chek = "chekkit" in " ".join(dom).lower()
    print("- %s%s" % (tid, "  [chekkit allow-listed]" if chek else ""))
print("\nSUMMARY browser_missing=%d browser_ok=%d scanned=%d" % (len(need), len(have), total))
