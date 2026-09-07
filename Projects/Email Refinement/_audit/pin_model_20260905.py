#!/usr/bin/env python3
"""Pin model: claude-sonnet-5 on the two scheduled tasks created 2026-09-05 (Email Dept plan file 19).
Per the scheduled-task-models skill, every scheduled task must carry a model: line in frontmatter.
Idempotent; backs up before writing."""
import os, re, shutil

S = os.path.expanduser("~/Documents/Claude/Scheduled")
for t in ("brevo-stage-next-quarter", "brevo-engaged-v2-refresh"):
    p = os.path.join(S, t, "SKILL.md")
    if not os.path.exists(p):
        print("MISSING", t); continue
    s = open(p, encoding="utf-8").read()
    if re.search(r"^model:", s, re.M):
        print("already pinned:", t); continue
    b = p + ".bak-pre-modelpin-20260905"
    if not os.path.exists(b):
        shutil.copy2(p, b)
    s = s.replace("\n---\n", "\nmodel: claude-sonnet-5\n---\n", 1)
    open(p, "w", encoding="utf-8").write(s)
    print("pinned:", t)

for t in ("brevo-stage-next-quarter", "brevo-engaged-v2-refresh"):
    p = os.path.join(S, t, "SKILL.md")
    if os.path.exists(p):
        head = "".join(open(p, encoding="utf-8").readlines()[:6])
        print("---", t, "---\n" + head)
