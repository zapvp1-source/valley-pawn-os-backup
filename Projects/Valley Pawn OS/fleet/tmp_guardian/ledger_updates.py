#!/usr/bin/env python3
import re, sys

path = sys.argv[1]
with open(path, encoding="utf-8") as f:
    lines = f.readlines()

updates = [
("| 2026-11-06 16:19 ET (native) | ebay-efficiency-weekly |",
 " UNRECOVERED 2026-11-07 (fleet-guardian 21:45 pass) -- real miss confirmed via output (Rule 12): no \"eBay Efficiency — Weekly\" post in #ebay-performance since 10/30 (checked live). Root cause found: this agent's script lives OUTSIDE fleet governance at /Users/joshuadavis/ebay_efficiency_weekly.py (not under Valley Pawn OS/bin/, no OS_DIR/backup convention, logs to ~/ebay_efficiency_weekly.err which this session's connected folders can't reach and which isn't on the host_queue allowlist) -- not rerun this pass for lack of a safe, allow-listed entrypoint. Needs a future touch: migrate the script into bin/ under governance (or add it to fleet/host_queue_allowlist.txt + fleet/rerun_manifest.json rerun_safe -- pure internal report, no external contact) so it's recoverable next time."),

("| 2026-11-06 18:05 ET (native) | fleet-medic |",
 " COVERED 2026-11-07 (fleet-guardian 21:45 pass) -- host_diag.sh agents (21:46 ET) shows 0 agents at exit 126 fleet-wide; same TCC/exit-126 wave already closed DONE for 10+ other agents in HUMAN_QUEUE.md (11/1-11/4), self-healed by fleet-medic's own retry."),

("| 2026-11-06 21:35 ET (native) | storetraffic-nightly |",
 " COVERED 2026-11-07 (fleet-guardian 21:45 pass) -- design-expected: the task's own message says these store-days are left out automatically and counters self-restart (same informational pattern as the 11/5 CHANGELOG calibration note), not a failure."),

("| 2026-11-06 21:55 ET (native) | missed-call-text |",
 " COVERED 2026-11-07 (fleet-guardian 21:45 pass) -- fleet/receipts/missed-call-text.jsonl shows many successful posts throughout 2026-11-07 (through 17:49 ET), confirming the single 21:55 ET Zoom-API read was transient and self-healed on the next run."),

("| 2026-11-07 02:10 ET (native) | fleet-doctor |",
 " COVERED 2026-11-07 (fleet-guardian 21:45 pass) -- cross-checked against FIELD_SCORECARD.md + HUMAN_QUEUE.md: flagged items are the same historical/already-tracked noise as the 10/22-11/6 occurrences of this same weekly aggregate, no new gap found."),

("| 2026-11-07 04:05 ET (native) | bravo-daily-gl | Daily Bravo posting for Culpeper 2026-11-05",
 " QUEUED 2026-11-07 (fleet-guardian 21:45 pass) -- Bravo-driving = verify-only + guardian hard limit, no rerun attempted. Real current state (fleet/state/bravo_daily_gl/STATUS.md) is worse than previously tracked: ALL 5 stores now unposted for 2026-11-05 (3 tries each, same UIA click wall) AND all 5 for 2026-11-06 (\"not posted to accounting yet\", 1 try each) -- bumped the existing 2026-11-05 HUMAN_QUEUE row with this expanded 2-day/5-store backlog."),
("| 2026-11-07 04:05 ET (native) | bravo-daily-gl | Daily Bravo posting for Harrisonburg 2026-11-05",
 " QUEUED 2026-11-07 (fleet-guardian 21:45 pass) -- same backlog as the Culpeper row above (all 5 stores, 2026-11-05 + 2026-11-06); bumped the existing HUMAN_QUEUE row once, not once per store."),
("| 2026-11-07 04:05 ET (native) | bravo-daily-gl | Daily Bravo posting for Lexington 2026-11-05",
 " QUEUED 2026-11-07 (fleet-guardian 21:45 pass) -- same backlog as the Culpeper row above (all 5 stores, 2026-11-05 + 2026-11-06); bumped the existing HUMAN_QUEUE row once, not once per store."),
("| 2026-11-07 04:05 ET (native) | bravo-daily-gl | Daily Bravo posting for Roanoke 2026-11-05",
 " QUEUED 2026-11-07 (fleet-guardian 21:45 pass) -- same backlog as the Culpeper row above (all 5 stores, 2026-11-05 + 2026-11-06); bumped the existing HUMAN_QUEUE row once, not once per store."),
("| 2026-11-07 04:05 ET (native) | bravo-daily-gl | Daily Bravo posting for Waynesboro 2026-11-05",
 " QUEUED 2026-11-07 (fleet-guardian 21:45 pass) -- same backlog as the Culpeper row above (all 5 stores, 2026-11-05 + 2026-11-06); bumped the existing HUMAN_QUEUE row once, not once per store."),

("| 2026-11-07 07:35 ET (native) | conductwatch-report |",
 " COVERED 2026-11-07 (fleet-guardian 21:45 pass) -- same Slack bot scope gap (conversations.history: missing_scope) as 11/1-11/6, now 7th consecutive day; bumped the existing HUMAN_QUEUE.md Slack-scope row, Last hit -> 2026-11-07."),

("| 2026-11-07 08:30 ET (native) | oura-daily-import |",
 " QUEUED 2026-11-07 (fleet-guardian 21:45 pass) -- same upstream Oura-sync issue as 10/21 on; bumped the existing HUMAN_QUEUE.md row, Last hit -> 2026-11-07. No rerun attempted (confirmed upstream data per the 10/21 host-queue precedent)."),

("| 2026-11-07 10:30 ET (native) | daily-dress-code-check |",
 " RECOVERED 2026-11-07 (fleet-guardian 21:45 pass) -- verified via real output: #basics shows \"Dress Code Check — Saturday, November 7, 2026 @ 12:58 PM\", all 5 stores clean. The task's own retry logic succeeded later in the day after this and the other same-morning attempts hit the shared-Chrome-profile contention."),
("| 2026-11-07 10:40 ET (native) | daily-dress-code-check |",
 " RECOVERED 2026-11-07 -- duplicate of the 10:30 ET row; same successful 12:58 PM post covers it."),
("| 2026-11-07 11:25 ET (native) | daily-dress-code-check |",
 " RECOVERED 2026-11-07 -- duplicate of the 10:30 ET row; same successful 12:58 PM post covers it."),
("| 2026-11-07 12:10 ET (native) | daily-dress-code-check |",
 " RECOVERED 2026-11-07 -- duplicate of the 10:30 ET row; same successful 12:58 PM post covers it."),

("| 2026-11-07 10:31 ET (native) | daily-cloudcover-check |",
 " UNRECOVERED 2026-11-07 (fleet-guardian 21:45 pass) -- confirmed real miss: no Cloud Cover post in #basics for Sat Nov 7 (most recent is Fri 11/6 10:00 AM); FIELD_SCORECARD.md confirms window closed 13:25 ET, nothing found. Rerun-safe per manifest, but the script's own POST_CUTOFF (13:25 ET) refuses to post a stale snapshot past that time, and it is now 21:45 ET -- no rerun attempted (would not post by design). Same shared-Chrome-profile-hang pattern as 2026-11-05, now a 2nd occurrence (dress-code recovered today, cloudcover did not) -- bumped the HUMAN_QUEUE.md Chrome-profile row; per Rule 15 clause 2 this now needs a real design fix on a future hardening touch, not another retry."),
("| 2026-11-07 10:40 ET (native) | daily-cloudcover-check |",
 " UNRECOVERED 2026-11-07 -- duplicate of the 10:31 ET row above; same root cause and resolution."),
("| 2026-11-07 11:25 ET (native) | daily-cloudcover-check |",
 " UNRECOVERED 2026-11-07 -- duplicate of the 10:31 ET row above; same root cause and resolution."),
("| 2026-11-07 12:10 ET (native) | daily-cloudcover-check |",
 " UNRECOVERED 2026-11-07 -- duplicate of the 10:31 ET row above; same root cause and resolution."),
("| 2026-11-07 12:56 ET (native) | daily-cloudcover-check |",
 " UNRECOVERED 2026-11-07 -- duplicate of the 10:31 ET row above; same root cause and resolution."),

("| 2026-11-07 10:13 ET (native) | fleet-medic |",
 " COVERED 2026-11-07 (fleet-guardian 21:45 pass) -- host_diag.sh agents (21:46 ET) shows 0 agents at exit 126 fleet-wide; same self-healed TCC/exit-126 wave as the 11/6 18:05 ET row above."),
("| 2026-11-07 17:05 ET (native) | fleet-medic |",
 " COVERED 2026-11-07 (fleet-guardian 21:45 pass) -- host_diag.sh agents (21:46 ET) shows 0 agents at exit 126 fleet-wide; same self-healed TCC/exit-126 wave."),

("| 2026-11-07 11:17 ET | bald-rock-guest-reviews |",
 " Re-checked 2026-11-07 21:45 ET (fleet-guardian) -- still not recoverable (Airbnb hosting pages checked earlier today, 503); guest-facing/verify-only per rerun_manifest.json, not re-driven by the guardian. Task's own daily 11:00 ET cron will retry naturally tomorrow; 2 days remain before Camille Hathaway's 14-day window lapses (11/9) -- will escalate to HUMAN_QUEUE if still unresolved after tomorrow's retry."),

("| 2026-11-07 12:13 ET (native) | chekkit-ai-responder |",
 " QUEUED 2026-11-07 (fleet-guardian 21:45 pass) -- confirmed via bin/chekkit_ai_responder.py: it requires a real Anthropic API key in Keychain \"vp-agent-anthropic-key\" or ~/.vp_secrets/anthropic.json, currently missing. New Life OS/HUMAN_QUEUE.md row added (human-only, not urgent)."),

("| 2026-11-07 12:46 ET (cowork, Social Media session) | fleet-guardian-cowork |",
 " RESOLVED 2026-11-07 (this 21:45 pass) -- this exact Cowork/Social-Media-session binding DOES have full Mac access this run (get_device_info + device_bash succeeded, mounts Projects+Refine Social Media rw) and completed Steps 1-4 end to end via the documented Host Job Queue workaround (task_preflight.py / reg_shape.py / host_diag.sh via fleet/host_queue/), reading the real scheduler registry (232 tasks, 2 enabled) and launchd agent states, and recovering/verifying today's misses. The 12:46 ET firing earlier today evidently ran with the Mac bridge not linked (desktop app closed/offline at that moment) -- intermittent, not a permanent session/device misconfiguration; no task-routing change needed. Will keep documenting if it recurs."),

("| 2026-11-07 12:56 ET (native) | daily-cloudcover-check | The Cloud Cover music check could not open its automation browser",
 ""),

("| 2026-11-07 21:35 ET (native) | storetraffic-nightly |",
 " COVERED 2026-11-07 (fleet-guardian 21:45 pass) -- design-expected, same as the 11/6 21:35 ET row: self-restart behavior, not a failure."),
]

out = []
applied = set()
for ln in lines:
    stripped = ln.rstrip("\n")
    matched = False
    for i, (sub, resolution) in enumerate(updates):
        if i in applied:
            continue
        if sub and sub in stripped and stripped.endswith("| OPEN |"):
            if resolution == "":
                out.append(ln)
            else:
                out.append(stripped + resolution + "\n")
            applied.add(i)
            matched = True
            break
    if not matched:
        out.append(ln)

with open(path, "w", encoding="utf-8") as f:
    f.writelines(out)

print("applied", len(applied), "of", len(updates))
missing = [updates[i][0] for i in range(len(updates)) if i not in applied]
for m in missing:
    print("MISSED:", m)
