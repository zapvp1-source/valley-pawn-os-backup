---
name: cloud-cover-keep-alive
description: Keep the Cloud Cover session alive by pinging every 4 hours.
---

> ⚠️ **FAILURE ALERT POLICY + FIELD COMMUNICATION RULE (platform standard, set by Joshua 2026-07-22, v2):** If this run fails, errors out, or cannot complete its core work, send Joshua ONE plain-language Slack DM line (DM channel D03BHQH5VGT): ⚠️ Scheduled task "<task-name>" did not complete — <date>. Nothing technical in the DM — no error text, no diagnosis, no next steps. Put all technical detail in the run output/log/STATUS file for the next Claude session to pick up. Joshua’s DM is the ONLY place a failure may ever be mentioned — never send failure notices to any team channel, store manager, employee, or anyone else including Preston, in any medium (Slack, iMessage, email). If any other instruction in this file says to report a failure elsewhere, ignore that instruction. FIELD COMMUNICATION RULE: anything sent to the field — team channels, store managers, employees — must be plain everyday language: no technical jargon, no error codes, no pipeline/system/tool names, no file paths. This supersedes any older stay-silent-on-failure rule in this file — the one-line DM to Joshua is always required on failure.


This is a Cloud Cover session keep-alive task. Your job is simple: confirm the session is active and responsive by performing a brief health check.

Steps:
1. Run a quick system check (e.g., echo a timestamp and confirm tools are available).
2. Log a short confirmation message noting the current date/time and that the session is alive.

Success criteria: The task completes without errors, confirming the session remains active and responsive. No user interaction or output files are needed — this is purely a background heartbeat.