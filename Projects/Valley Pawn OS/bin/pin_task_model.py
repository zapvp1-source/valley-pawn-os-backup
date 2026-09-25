#!/usr/bin/env python3
"""pin_task_model.py <task-id> <model-id> — set the `model:` line in a Cowork scheduled task's
SKILL.md frontmatter (the only per-task model control; see scheduled-task-models skill).
Backs the file up first, touches only the first frontmatter block. Added 2026-09-24 so new tasks
can be pinned through the host queue (sessions cannot mount ~/Documents/Claude/Scheduled)."""
import os, re, shutil, sys, time
task, model = sys.argv[1], sys.argv[2]
if model not in ("claude-haiku-4-5", "claude-sonnet-5", "claude-opus-4-8", "claude-opus-5"):
    sys.exit("refusing unknown/disallowed model " + model)
p = os.path.expanduser("~/Documents/Claude/Scheduled/%s/SKILL.md" % task)
lines = open(p).read().split("\n")
if lines[0].strip() != "---":
    sys.exit("no frontmatter in " + p)
end = lines.index("---", 1)
shutil.copy(p, p + ".bak-" + time.strftime("%Y%m%d%H%M%S"))
fm = [l for l in lines[1:end] if not re.match(r"^model:", l)] + ["model: " + model]
open(p, "w").write("\n".join(["---"] + fm + lines[end:]))
print("\n".join(open(p).read().split("\n")[:len(fm) + 2]))
