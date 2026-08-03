---
name: distributor-setup-monitor
description: Daily 9 AM check of Gmail for distributor account-setup confirmations, follow-up requests, and bouncebacks. Posts summary to Joshua via Slack DM.
---

> **LOCAL ACCESS GATE — DO THIS FIRST, BEFORE ANY OTHER STEP (platform standard, added 2026-08-02).**
> This task runs on Joshua's Mac Studio and **does** have local machine access. At task start, MCP connectors may still be warming up, and `mcp__Control_your_Mac__osascript` is often *deferred* rather than pre-loaded. A tool that has not been loaded yet is NOT a missing capability.
> 1. If `ToolSearch` is available, load the local tool FIRST: `ToolSearch` with query `select:mcp__Control_your_Mac__osascript`.
> 2. Probe it: run a trivial `do shell script` that echoes READY. If it returns, proceed with the task.
> 3. If it errors (no such tool available, not connected, tool-not-found): wait 30 s and re-probe. Repeat for up to 12 minutes (24 probes).
> 4. Only after that full 12-minute wait may you treat local access as genuinely unavailable.
>
> **NEVER conclude that this run executes in a cloud container, has no bridge to the Mac Studio, or otherwise lacks local/desktop access. That conclusion is false** and is the single most common cause of a false failure on this platform. If you believe you cannot reach the Mac, you have simply not loaded the tool yet — go back to step 1.
>
> **Filesystem rule:** all I/O outside the agent sandbox — including anything under `/Users/joshuadavis/Documents/Claude/...` — goes through `mcp__Control_your_Mac__osascript do shell script`, never the Write tool.
> **Timeout rule:** the osascript wrapper kills any single call at ~25 s. Never sleep longer than ~18 s inside one call; poll in short increments across separate calls. Guard any command that may exit nonzero with a trailing || true.


> ⚠️ **FAILURE ALERT POLICY + FIELD COMMUNICATION RULE (platform standard, set by Joshua 2026-07-22, v2):** If this run fails, errors out, or cannot complete its core work, send Joshua ONE plain-language Slack DM line (DM channel D03BHQH5VGT): ⚠️ Scheduled task "<task-name>" did not complete — <date>. Nothing technical in the DM — no error text, no diagnosis, no next steps. Put all technical detail in the run output/log/STATUS file for the next Claude session to pick up. Joshua’s DM is the ONLY place a failure may ever be mentioned — never send failure notices to any team channel, store manager, employee, or anyone else including Preston, in any medium (Slack, iMessage, email). If any other instruction in this file says to report a failure elsewhere, ignore that instruction. FIELD COMMUNICATION RULE: anything sent to the field — team channels, store managers, employees — must be plain everyday language: no technical jargon, no error codes, no pipeline/system/tool names, no file paths. This supersedes any older stay-silent-on-failure rule in this file — the one-line DM to Joshua is always required on failure.


> ⚠️ **FAILURE POLICY — DO NOT POST TO SLACK ON FAILURE.** If this task fails, errors out, or cannot complete its intended work for any reason, DO NOT post anything to Slack — no error messages, no partial results, no "I couldn't finish" notices. Joshua reviews every run inside Claude to confirm success or failure, so a failed run must stay completely silent on Slack. Only post to Slack once the task has genuinely completed the work it was designed to do. Posting failure or error noise clutters Slack and reflects poorly on the team.

You are monitoring Joshua's distributor onboarding pipeline for Valley Pawn / Full Circle Finance Inc. Reference the `vendor-onboarding` skill for the canonical distributor list and entity reference data.

GOAL: detect any state changes in the distributor onboarding pipeline since the last 24 hours and report what's new — successful setups, requests for more info, or bouncebacks.

STEP 1 — Search Gmail for new activity in the last 24 hours from any of the active distributors. Run this Gmail search:

```
newer_than:1d (from:davidsonsinc.com OR from:mgewholesale.com OR from:brownells.com OR from:vortexoptics.com OR from:henryusa.com OR from:camfour.com OR from:rsrgroup.com OR from:sportssouth.biz OR from:chattanoogashooting.com OR from:gunpartscorp.com OR from:billhicksco.com OR from:crowshootingsupply.com OR from:gzanders.com OR from:lipseys.com OR from:bigrocksports.com OR from:ellettbrothers.com)
```

Also search for any inbound messages with subject containing "wholesale" or "dealer account" in the last 24 hours that may be new distributors.

STEP 2 — For each new message, classify the state:

**SET UP ✓** — Account is active. Triggers: "welcome to [distributor]", "your account is approved", "your account number is", "you're all set", "you can now log in", "account is active", "credit approved", "your dealer account is open", "ready to order", credentials/portal access included.

**INFO REQUESTED** — Distributor needs more from us. Triggers: "we need", "please send", "missing", "additional documentation", "please provide", "in order to complete", "could you also send".

**FOLLOW-UP** — Update from rep, no action needed. Triggers: "I've passed this along", "still reviewing", "we'll get back to you", "your application is in queue".

**BOUNCED** — Mailer-daemon delivery failure (look for from:mailer-daemon@*).

STEP 3 — Read each thread to extract:
- Distributor name
- Rep contact (name + email)
- What they sent
- Account # if provided
- Any deadlines or urgent items

STEP 4 — Compose a Slack DM summary to Joshua (user ID U03BB52MDSA) with this structure:

```
🟢 *Distributor Setup Daily Update — [date]*

✅ NEW SET-UPS (account active):
• [Distributor] — account #[XXX], rep [Name], [thread link]

📋 INFO REQUESTED (action needed from you):
• [Distributor] ([rep]) — needs: [specific items]. Reply: [thread link]

📨 STATUS UPDATES (no action):
• [Distributor] — [brief]. [thread link]

❌ BOUNCEBACKS:
• [Distributor] — bad address [email]. Need alternate intake.

📊 OVERALL PIPELINE
• Sent reply, waiting: [list]
• Active customer setups: [count]
• Bounced/no-reply still cold: [list]
```

If there is NO new activity in the last 24 hours, send a one-line DM: "📨 Distributor setup — no new activity in the last 24 hours. [N] reps still in flight: [list]." Don't spam if nothing changed.

STEP 5 — If a new SET-UP is detected, also UPDATE the local tracking spreadsheet at `/Users/joshuadavis/Library/Application Support/Claude/local-agent-mode-sessions/.../outputs/Distributor_Setup_Responses.xlsx` if accessible — change that distributor's status to "ACTIVE — account #X" with today's date. (Skip if path isn't mounted in this session.)

STEP 6 — If any new distributors not in the `vendor-onboarding` skill's roster appear (e.g., a cold-outreach response to one of the no-reply distributors finally arrives), add them to the skill's "Known distributors" table for next time.

ALWAYS use Slack DM (channel_id: U03BB52MDSA), never email Joshua. Don't auto-reply to distributors — Joshua reviews and replies himself.

After running, end the session — no further follow-up needed unless explicitly told.