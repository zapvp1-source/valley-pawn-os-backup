---
name: monday-bravo-reminder
description: Monday morning reminder for Joshua to paste the Bravo Company Performance report into Mac Chrome
---

> ⚠️ **FAILURE ALERT POLICY + FIELD COMMUNICATION RULE (platform standard, set by Joshua 2026-07-22, v2):** If this run fails, errors out, or cannot complete its core work, send Joshua ONE plain-language Slack DM line (DM channel D03BHQH5VGT): ⚠️ Scheduled task "<task-name>" did not complete — <date>. Nothing technical in the DM — no error text, no diagnosis, no next steps. Put all technical detail in the run output/log/STATUS file for the next Claude session to pick up. Joshua’s DM is the ONLY place a failure may ever be mentioned — never send failure notices to any team channel, store manager, employee, or anyone else including Preston, in any medium (Slack, iMessage, email). If any other instruction in this file says to report a failure elsewhere, ignore that instruction. FIELD COMMUNICATION RULE: anything sent to the field — team channels, store managers, employees — must be plain everyday language: no technical jargon, no error codes, no pipeline/system/tool names, no file paths. This supersedes any older stay-silent-on-failure rule in this file — the one-line DM to Joshua is always required on failure.


Send Joshua a friendly reminder that it's Monday morning and time to pull the weekly store performance rankings. Ask him to:

1. Open the Bravo Company Performance report in his Parallels Windows VM
2. Copy the SSRS URL and paste it into Chrome on his Mac side

Once he does that, the monday-store-rankings scheduled task will handle pulling the data, building the spreadsheet, and posting to the Slack #performance channel.

Keep the message short and casual — something like: "Hey Joshua — it's Monday! Time for the weekly store rankings. When you're ready, pull the Bravo Company Performance report and paste the URL into Mac Chrome so I can grab the data and post the rankings to #performance."