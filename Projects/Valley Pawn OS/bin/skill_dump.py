#!/usr/bin/env python3
"""skill_dump.py <task> [max_chars] — print a scheduled task's SKILL.md (read-only; the sandbox cannot
see ~/Documents/Claude/Scheduled). Default 12000 chars."""
import os, sys
p=os.path.expanduser("~/Documents/Claude/Scheduled/%s/SKILL.md" % sys.argv[1])
n=int(sys.argv[2]) if len(sys.argv)>2 else 12000
print(open(p, errors="replace").read()[:n] if os.path.isfile(p) else "MISSING "+p)
