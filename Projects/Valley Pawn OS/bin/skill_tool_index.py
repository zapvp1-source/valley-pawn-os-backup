#!/usr/bin/env python3
"""skill_tool_index.py — write fleet/skill_tool_index.json: for every MCP server id (and named families
like slack/gmail/drive/gusto/qbo/chrome), which scheduled tasks name it in their SKILL.md.
WHY (2026-09-29): connector-health-daily must list the tasks a failing connector would break, but a
scheduled session cannot see ~/Documents/Claude/Scheduled/. This index is readable from Projects."""
import json, os, re, glob, datetime as dt
S = os.path.expanduser("~/Documents/Claude/Scheduled")
OUT = os.path.expanduser("~/Documents/Claude/Projects/Valley Pawn OS/fleet/skill_tool_index.json")
FAM = {"slack": r"slack_", "gmail": r"search_threads|create_draft|get_thread", "drive": r"2ce817f2|search_files|create_file",
       "gusto": r"ca1b6a08|list_employees", "qbo": r"37675e3a|quickbooks", "calendar": r"ae0e7c34|list_events",
       "chrome": r"claude-in-chrome", "docusign": r"8ff1eb8f", "canva": r"a246b176", "wordpress": r"40f0bfed|wpcom"}
idx = {"generated_at": dt.datetime.now().isoformat(timespec="seconds"), "servers": {}, "families": {k: [] for k in FAM}}
for p in sorted(glob.glob(os.path.join(S, "*", "SKILL.md"))):
    t = os.path.basename(os.path.dirname(p)); b = open(p, errors="replace").read()
    for srv in set(re.findall(r"mcp__([0-9a-f-]{36}|[A-Za-z_-]+)__", b)):
        idx["servers"].setdefault(srv, []).append(t)
    for fam, rx in FAM.items():
        if re.search(rx, b): idx["families"][fam].append(t)
tmp = OUT + ".tmp"; json.dump(idx, open(tmp, "w"), indent=1); os.replace(tmp, OUT)
print("indexed", sum(len(v) for v in idx["families"].values()), "family refs;", len(idx["servers"]), "servers")
