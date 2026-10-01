#!/usr/bin/env python3
"""task_triage.py — one line per ENABLED scheduled task: what its SKILL.md relies on, to decide what can
become a native agent. Read-only. Writes fleet/task_triage.json and prints a compact table."""
import glob, json, os, re
H = os.path.expanduser("~")
REG = sorted(glob.glob(H + "/Library/Application Support/Claude/local-agent-mode-sessions/*/*/scheduled-tasks.json"), key=os.path.getmtime)[-1]
tasks = [t for t in json.load(open(REG))["scheduledTasks"] if t.get("enabled")]
F = {
 "script": r"python3 [^\n]*\.py|bash [^\n]*\.sh|-m vp_social|comms_engine|_helper\.py",
 "slack_r": r"slack_read_channel|slack_search|conversations\.history",
 "slack_w": r"slack_send_message|outbox",
 "gmail": r"search_threads|get_thread|create_draft|Gmail",
 "drive": r"search_files|create_file|Google Drive|Drive folder",
 "gusto": r"list_employees|Gusto|time_sheet|list_time_records",
 "qbo": r"QuickBooks|QBO|qbo_",
 "browser": r"claude-in-chrome|navigate|browser_batch|Claude_Browser",
 "bravo": r"Bravo Data Extraction|bravo_pull|triggers/",
 "vision": r"photo|screenshot|image|camera",
 "judgment": r"recommend|summari[sz]e|draft|write a|decide|judg|evaluate|assess|flag anything|explain",
 "artifact": r"Artifact tool|artifact",
 "api": r"api\.|API v|Graph API|Trading API|REST",
}
rows = []
for t in sorted(tasks, key=lambda t: t["id"]):
    p = os.path.join(H, "Documents/Claude/Scheduled", t["id"], "SKILL.md")
    b = open(p, errors="replace").read() if os.path.isfile(p) else ""
    feats = [k for k, rx in F.items() if re.search(rx, b, re.I)]
    rows.append({"id": t["id"], "cron": t.get("cronExpression"), "bytes": len(b), "feats": feats,
                 "desc": (t.get("description") or "")[:150]})
json.dump(rows, open(os.path.join(H, "Documents/Claude/Projects/Valley Pawn OS/fleet/task_triage.json"), "w"), indent=1)
for r in rows:
    print("%-42s %-16s %s" % (r["id"][:42], (r["cron"] or "")[:16], ",".join(r["feats"])))
print("TOTAL enabled:", len(rows))
