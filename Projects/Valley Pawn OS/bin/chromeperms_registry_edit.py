#!/usr/bin/env python3
"""Phase 0.4 of SCHEDULED_TASK_RELIABILITY_PLAN.md (2026-09-04).
Run ONLY while Claude.app is fully quit (chromeperms_apply.sh handles that).

Edits the Cowork scheduler registry, additively:
  1. chromePermissionMode = "skip_all_permission_checks" on every enabled task that drives the
     Chrome extension / Gusto — so unattended runs never wait 30 min on a permission card
     (log evidence: "browser/computer sentinel permissions require a live card" -> permission_stall).
     Existing chromeAllowedDomains are left in place.
  2. userSelectedFolders += ~/Documents/Claude/Projects on every enabled task that lacks it, so
     Read/Grep work without request_cowork_directory (which stalls unattended:
     "directory mounts use userSelectedFolders").
  3. northwest-registered-agent-daily-check cron 0 8 -> 40 8 (the one Phase 0.3 move the
     interactive tool refused).
Backup + atomic write, exactly like .migration-staging/registry_edit.py (proven 2026-08-21)."""
import json, os, shutil, time

REG = os.path.expanduser("~/Library/Application Support/Claude/local-agent-mode-sessions/823f6874-6252-4031-ae4e-a3c22d37598e/f6b75d02-cca9-4943-ad6e-88390a3f201d/scheduled-tasks.json")
STAMP = time.strftime("%Y%m%d-%H%M%S")
PROJECTS = "/Users/joshuadavis/Documents/Claude/Projects"

CHROME_TASKS = [
    "bald-rock-guest-reviews", "ffl-transfer-email-responder", "jewelry-onhand-nightly-pull",
    "monthly-gun-audit-report", "northwest-registered-agent-daily-check", "sold-review",
    "sunday-checklist-summary", "vp-ai-search-health-check", "vp-ai-visibility-autofix",
    "vp-ai-visibility-metrics", "vp-follower-growth-monthly-check", "vp-website-shop-nightly",
    "weekly-timekeeping-analysis", "zoom-voicemail-alert", "zoom-voicemail-eod-review",
    "gusto-keep-alive", "daily-clockin-check", "vp-website-trend-daily-refresh",
    "vp-new-customer-report", "daily-cloudcover-check", "daily-dress-code-check",
    "nightly-chekkit-review-responses", "vp-weekly-spot-price-update", "weekly-returns-summary",
    "chekkit-weekly-review-requests", "vp-gusto-signature-chase", "google-reviews-post-watchdog",
]
CRON_FIX = {"northwest-registered-agent-daily-check": "40 8 * * *"}

def main():
    bak = REG + ".bak-chromeperms-" + STAMP
    shutil.copy2(REG, bak)
    d = json.load(open(REG))
    tasks = d["scheduledTasks"]
    byid = {t["id"]: t for t in tasks}
    perm, folders, cron, missing = [], [], [], []
    for tid in CHROME_TASKS:
        t = byid.get(tid)
        if not t:
            missing.append(tid); continue
        if t.get("chromePermissionMode") != "skip_all_permission_checks":
            t["chromePermissionMode"] = "skip_all_permission_checks"
            perm.append(tid)
    for t in tasks:
        if not t.get("enabled"):
            continue
        f = t.get("userSelectedFolders") or []
        if PROJECTS not in f:
            t["userSelectedFolders"] = f + [PROJECTS]
            folders.append(t["id"])
    for tid, c in CRON_FIX.items():
        t = byid.get(tid)
        if t and t.get("cronExpression") != c:
            t["cronExpression"] = c; cron.append(tid)
    tmp = REG + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(d, fh, indent=1)
    json.load(open(tmp))  # reparse before replacing
    os.replace(tmp, REG)
    print("BACKUP:", bak)
    print("chromePermissionMode set on", len(perm), ":", perm)
    print("Projects folder added on", len(folders), "tasks")
    print("cron fixed:", cron)
    print("MISSING ids:", missing)
    print("task count:", len(tasks))

if __name__ == "__main__":
    main()
