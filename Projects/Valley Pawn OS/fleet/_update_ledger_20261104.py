import re, shutil, datetime

path = "/sessions/rcw-01h5r2c7csd4rydsrn3vu1gz/mnt/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md"
backup = path.replace(".md", ".md.bak-guardian-20261104-1245")
shutil.copy(path, backup)

with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

edits = {
    "2026-11-04 10:28 ET (native) | daily-cloudcover-check":
        " RECOVERED 2026-11-04 (fleet-guardian 12:45 ET pass) -- re-ran via bin/vp_browser.py launch-retry fix (backup .bak-pre-launchretry-20261104), confirmed posted 11:34 ET per CHANGELOG 2026-11-04 12:15 ET; verified against real output, not run record.\n",
    "2026-11-04 10:33 ET (native) | daily-dress-code-check":
        " RECOVERED 2026-11-04 (fleet-guardian 12:45 ET pass) -- re-ran via bin/vp_browser.py launch-retry fix, confirmed posted 11:33 ET per CHANGELOG 2026-11-04 12:15 ET; verified against real output.\n",
    "2026-11-04 10:36 ET (native) | dress-code-check | REPEAT FAILURE":
        " RECOVERED 2026-11-04 (fleet-guardian 12:45 ET pass) -- root cause was the exit-126 'Interrupted system call' launch issue, fixed fleet-wide via bin/fleet_medic.py R5 retry + bin/vp_browser.py launch-retry (backups .bak-pre-126retry-20261104 / .bak-pre-launchretry-20261104); task posted successfully 11:33 ET, confirmed via real output, not a run record.\n",
    "2026-11-04 02:10 ET (native) | fleet-doctor":
        " COVERED 2026-11-04 (fleet-guardian 12:45 ET pass) -- the errors/quiet jobs this nightly aggregate flagged overlap with the 18-task exit-126 'Interrupted system call' cluster (11/1-11/4), already root-caused and fixed fleet-wide today (CHANGELOG 2026-11-04 12:15 ET; all 18 HUMAN_QUEUE rows closed same day); no residual Joshua action needed, consistent with this report's history of resolving via same-day fixes (10/22, 10/24, 10/31).\n",
    "2026-11-04 07:35 ET (native) | conductwatch-report":
        " QUEUED 2026-11-04 (fleet-guardian 12:45 ET pass) -- 4th consecutive day (11/1-11/4), identical root cause confirmed 11/3 (Slack `conversations.history: missing_scope` on its duplicate-guard read, OAuth scope gap on the vp-ops bot). Reclassifying this NEEDS_HUMAN:no row as human-only based on the established root cause (not re-litigating it) -- folded into the existing files:write/conversations.history HUMAN_QUEUE row (Life OS/HUMAN_QUEUE.md line ~56), Last-hit bumped to 2026-11-04.\n",
    "2026-11-02 10:15 ET | scrap-monthly-bravo-manifest-stage":
        " SUPERSEDED 2026-11-04 (fleet-guardian 12:45 ET pass) -- superseded by the 2026-11-04 09:57 ET row below (both October Elemetal settlements have since arrived; blocker moved to Culpeper/Waynesboro opening their October gold buckets in Bravo).\n",
    "2026-11-03 09:48 ET | scrap-monthly-bravo-manifest-stage":
        " SUPERSEDED 2026-11-04 (fleet-guardian 12:45 ET pass) -- superseded by the 2026-11-04 09:57 ET row below (both October Elemetal settlements have since arrived; blocker moved to Culpeper/Waynesboro opening their October gold buckets in Bravo).\n",
    "2026-11-04 08:52 ET | northwest-registered-agent-daily-check":
        " QUEUED 2026-11-04 (fleet-guardian 12:45 ET pass) -- added a fresh [SIGN-IN] row to Life OS/HUMAN_QUEUE.md (same wall as 2026-10-24 and 2026-11-01, both previously resolved and now recurred); held for Login Day per the 2026-10-14 sign-in batching rule, not surfaced in any digest today.\n",
    "2026-11-04 09:57 ET | scrap-monthly-bravo-manifest-stage":
        " QUEUED 2026-11-04 (fleet-guardian 12:45 ET pass) -- added a Life OS/HUMAN_QUEUE.md row asking Joshua to have Culpeper and Waynesboro open their October 2026 gold / gold-with-stones buckets in Bravo.\n",
}

matched = {k: 0 for k in edits}
out = []
for line in lines:
    appended = False
    for key, note in edits.items():
        if key in line and line.rstrip().endswith("| OPEN |"):
            line = line.rstrip("\n") + note
            matched[key] += 1
            appended = True
            break
    out.append(line)

with open(path, "w", encoding="utf-8") as f:
    f.writelines(out)

print("backup:", backup)
for k, v in matched.items():
    print(v, k)
