#!/usr/bin/env python3
"""Cloud->local migration 2026-08-21: register 8 migrated tasks in the Cowork scheduler registry.
Run ONLY while Claude.app is quit (migrate.sh handles that). Atomic write + timestamped backup."""
import json, os, sys, time, shutil

REG = os.path.expanduser("~/Library/Application Support/Claude/local-agent-mode-sessions/823f6874-6252-4031-ae4e-a3c22d37598e/f6b75d02-cca9-4943-ad6e-88390a3f201d/scheduled-tasks.json")
SCHED = os.path.expanduser("~/Documents/Claude/Scheduled")
STAMP = time.strftime("%Y%m%d-%H%M%S")

NEW = {
    "precious-metals-settlement-handler": "0 9 * * *",
    "quarterly-capex-sweep":              "0 9 1 1,4,7,10 *",
    "bravo-preflight-relaunch":           "0 4 * * *",
    "monthly-ebay-ratings-sweep":         "0 10 1 * *",
    "hiring-inbox-watch":                 "0 10,12,14,16,18 * * 1-6",
    "monthly-scrap-rankings":             "30 4 1 * *",
    "vp-ai-visibility-autofix":           "30 9 * * 5",
    "vp-ai-search-autofix":               "30 8 * * 1",
}
SLACK_PERM = {"toolName": "mcp__f92ce7c6-0353-4419-8491-f0843b182ff2__slack_send_message"}
FOLDERS = ["/Users/joshuadavis/Documents/Claude", "/Users/joshuadavis/Documents/Claude/Projects"]

def main():
    bak = REG + ".bak-cloudmigration-" + STAMP
    shutil.copy2(REG, bak)
    shutil.copy2(REG, os.path.expanduser("~/Documents/Claude/Projects/.migration-staging/registry-backup-" + STAMP + ".json"))
    d = json.load(open(REG))
    existing = {t.get("id") for t in d["scheduledTasks"]}
    added, skipped, missing = [], [], []
    now = int(time.time() * 1000)
    for name, cron in NEW.items():
        skill = os.path.join(SCHED, name, "SKILL.md")
        if name in existing:
            skipped.append(name); continue
        if not os.path.isfile(skill):
            missing.append(name); continue
        d["scheduledTasks"].append({
            "id": name,
            "cronExpression": cron,
            "enabled": True,
            "filePath": skill,
            "createdAt": now,
            "userSelectedFolders": list(FOLDERS),
            "approvedPermissions": [dict(SLACK_PERM)],
        })
        added.append(name)
    tmp = REG + ".tmp"
    with open(tmp, "w") as f:
        json.dump(d, f, indent=1)
    # sanity: reparse before replacing
    json.load(open(tmp))
    os.replace(tmp, REG)
    print("ADDED:", added)
    print("SKIPPED(already registered):", skipped)
    print("MISSING SKILL.md (NOT added):", missing)
    print("BACKUP:", bak)

if __name__ == "__main__":
    main()
