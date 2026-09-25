#!/usr/bin/env python3
"""run_trace.py <task-id> [YYYY-MM-DD] [max_lines] — what the Claude app log says about one scheduled
task's run(s) on a day. Read-only. Prints the matching lines (timestamp + message, trimmed) so a
miss can be explained from the run's own record instead of from a guess (Rule 12 / Rule 19)."""
import os, re, sys, datetime as dt
task = sys.argv[1]
day = sys.argv[2] if len(sys.argv) > 2 else dt.date.today().isoformat()
mx = int(sys.argv[3]) if len(sys.argv) > 3 else 80
H = os.path.expanduser("~/Library/Logs/Claude")
hits = []
for name in sorted(os.listdir(H)) if os.path.isdir(H) else []:
    if not name.startswith("main"): continue
    p = os.path.join(H, name)
    try:
        for line in open(p, errors="replace"):
            if task in line and day in line:
                hits.append(line.rstrip()[:400])
    except OSError: pass
print("%d line(s) for %s on %s" % (len(hits), task, day))
for h in hits[-mx:]: print(h)
