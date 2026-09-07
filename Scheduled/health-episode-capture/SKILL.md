---
name: health-episode-capture
description: Daily 9:15 AM — turn Joshua's overnight notes-to-self and Health Log note into logged, Oura-cross-checked episodes.
model: claude-sonnet-4-5
---

Run Joshua's daily health episode capture. Domain 3 (Personal / Health). This is a quiet, low-touch task — most days there is nothing to do.

> ⚠️ FAILURE ALERT POLICY (platform standard, v2): if this run cannot complete its core work, send Joshua ONE plain-language Slack DM (channel D03BHQH5VGT): ⚠️ Scheduled task "health-episode-capture" did not complete — <date>. Nothing technical in the DM. All technical detail goes in the run output and in Health Optimization/STATUS.md. Never send failure notices anywhere else.

RUN ON THE HOST. Use `mcp__Control_your_Mac__osascript` with `do shell script` for every command. Do NOT use the workspace Bash tool or any `/sessions/*/mnt/` path — that mount deadlocks on this folder.

STEP 1 — run the capture script:
do shell script "cd '/Users/joshuadavis/Documents/Claude/Projects/Health Optimization' && python3 scripts/episode_capture.py 2>&1 | tail -20"

It reads (a) iMessages Joshua sent to himself (his own number and zapvp1@me.com) since the last run and (b) an Apple Note titled "Health Log", finds lines that look like an episode, pulls out time and severity, then cross-checks that night in the Oura database — hypnogram around the reported time, 5-minute heart-rate window, temperature deviation, SpO2, HRV, breathing-disturbance index, and the night's signature score. It appends to Episode_Log.csv and writes a detail file in episodes/. It is idempotent: an episode already logged for the same night and time is skipped.

STEP 2 — refresh the nights ledger (cheap, keeps last night scored):
do shell script "cd '/Users/joshuadavis/Documents/Claude/Projects/Health Optimization' && python3 scripts/night_signature.py 2>&1 | tail -3"

STEP 3 — report. If the capture logged nothing, your ENTIRE final message is exactly: "No new episodes." Nothing else — no preamble, no summary of what you checked.

If it DID log one or more episodes, send Joshua a short Slack DM (channel D03BHQH5VGT) in plain language, no jargon, no file paths, e.g.:
"Logged last night's episode — 2:20 AM, hot feet. You were in REM at that minute and woke out of it ten minutes later. Heart rate stayed flat at 62–68, body temp was up 0.2°, oxygen 93.9. Same pattern as August 13th."
Then your final message is one line saying what was logged.

Rules: never diagnose or speculate beyond what the data shows. Report what the numbers say and how it compares to the established pattern. Genuine medical interpretation is for Joshua and his doctors. If the script reports a night's Oura data has not synced yet, say the cross-check is pending for that night rather than guessing — do not treat it as a failure.