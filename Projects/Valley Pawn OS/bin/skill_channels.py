#!/usr/bin/env python3
"""skill_channels.py <task>... — list the Slack destinations a task's SKILL.md names (C…/D…/U… ids next to
slack_send_message or a channel mention). Read-only."""
import os, re, sys
for t in sys.argv[1:]:
    p = os.path.expanduser("~/Documents/Claude/Scheduled/%s/SKILL.md" % t)
    b = open(p, errors="replace").read() if os.path.isfile(p) else ""
    ids = sorted(set(re.findall(r"\b([CDU]0[A-Z0-9]{7,10})\b", b)))
    names = sorted(set(re.findall(r"(#[a-z0-9][a-z0-9_-]{2,40})", b)))[:8]
    print("%-40s ids=%s names=%s" % (t, ",".join(ids), ",".join(names)))
