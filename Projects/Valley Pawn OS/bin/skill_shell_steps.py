#!/usr/bin/env python3
"""skill_shell_steps.py <task>... — list the host commands a SKILL runs (python3/bash/osascript lines,
fenced code), so a conversion to a native agent reuses the SKILL's own steps. Read-only."""
import os, re, sys
RX = re.compile(r"(python3|/usr/bin/python3|bash |\.sh\b|\.py\b|osascript|do shell script|curl |sqlite3|tmutil|launchctl)")
for t in sys.argv[1:]:
    p = os.path.expanduser("~/Documents/Claude/Scheduled/%s/SKILL.md" % t)
    body = open(p, errors="replace").read() if os.path.isfile(p) else ""
    print("=" * 8, t, "(%d bytes)" % len(body))
    seen = set()
    for line in body.splitlines():
        l = line.strip()
        if RX.search(l) and not l.startswith(">") and len(l) < 400 and l not in seen:
            seen.add(l); print("  " + l[:260])
