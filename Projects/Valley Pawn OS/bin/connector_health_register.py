#!/usr/bin/env python3
"""Register the connector-health-daily scheduled task (2026-09-09).
Run ONLY while Claude.app is fully quit (connector_health_register.sh handles that).
Additive: appends one task entry if absent; touches nothing else. Backup + atomic write,
same pattern as chromeperms_registry_edit.py (proven 2026-09-04)."""
import json, os, shutil, time, glob
STAMP = time.strftime("%Y%m%d-%H%M%S")
cands = glob.glob(os.path.expanduser("~/Library/Application Support/Claude/local-agent-mode-sessions/*/*/scheduled-tasks.json"))
cands = [c for c in cands if ".bak" not in c]
assert len(cands) == 1, f"expected exactly one registry, found {cands}"
REG = cands[0]
TASK_ID = "connector-health-daily"
SKILL = f"/Users/joshuadavis/Documents/Claude/Scheduled/{TASK_ID}/SKILL.md"
assert os.path.exists(SKILL), f"SKILL.md missing at {SKILL}"
entry = {
  "id": TASK_ID,
  "cronExpression": "40 5 * * *",          # 05:40 ET daily — before the 6:30 Bravo corridor, no Chrome use
  "enabled": True,
  "filePath": SKILL,
  "createdAt": int(time.time()*1000),
  "lastRunAt": None,
  "lastScheduledFor": None,
  "userSelectedFolders": ["/Users/joshuadavis/Documents/Claude/Projects"],
  "chromePermissionMode": "skip_all_permission_checks",
  "approvedPermissions": [
    {"toolName": "mcp__00007879-ef17-43e5-9d59-6325cd2f0a31__list_labels"},
    {"toolName": "mcp__f92ce7c6-0353-4419-8491-f0843b182ff2__slack_read_user_profile"},
    {"toolName": "mcp__2ce817f2-5038-4cde-a6ab-8dedbe8abd84__list_recent_files"},
    {"toolName": "mcp__ae0e7c34-87de-4983-b24b-74cfc75cd4a1__list_calendars"},
    {"toolName": "mcp__37675e3a-e51c-470a-9eeb-b0aba96ba809__company_info"},
    {"toolName": "mcp__ca1b6a08-a5e1-43c1-b6ee-b11de4e2e8df__get_token_info"},
    {"toolName": "mcp__40f0bfed-dd3b-4c55-b43a-ad8386c9caa0__wpcom-user-sites"},
    {"toolName": "mcp__8ff1eb8f-1c43-4cbb-bcb3-9167c3c96cc7__getUserInfo"},
    {"toolName": "mcp__Control_your_Mac__osascript"},
  ],
}
bak = REG + ".bak-connector-health-" + STAMP
shutil.copy2(REG, bak)
d = json.load(open(REG))
ids = {t["id"] for t in d["scheduledTasks"]}
if TASK_ID in ids:
    print("already registered; no change"); raise SystemExit(0)
d["scheduledTasks"].append(entry)
tmp = REG + ".tmp"
with open(tmp, "w") as f: json.dump(d, f, indent=2)
os.replace(tmp, REG)
print("registered", TASK_ID, "backup:", bak, "total tasks:", len(d["scheduledTasks"]))
