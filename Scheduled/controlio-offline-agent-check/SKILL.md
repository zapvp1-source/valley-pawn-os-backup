---
name: controlio-offline-agent-check
description: Daily check of Controlio agents; flags any offline >48 hours and notifies Joshua.
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

Objective: Check Controlio for any monitoring agents that have been offline for more than 48 hours and report the results as a Claude notification to Joshua.

Context: Valley Pawn (Full Circle Finance Inc) runs Controlio employee monitoring on workstations across 5 stores: Culpeper, Waynesboro, Harrisonburg, Lexington, Roanoke. Controlio does not have a native "agent offline" alert rule, so this scheduled task fills that gap. Joshua is signed in at app.controlio.net as fullcirclepawn@gmail.com.

Steps:
1. Use the Claude-in-Chrome MCP to open https://app.controlio.net/system/users in an existing or new tab. If not signed in, stop and report that login is required — do NOT attempt to enter credentials.
2. Sort the Users list by "Last Seen" ascending (oldest first). Use `find` to locate the Last Seen column header and click it. Confirm ascending sort (arrow points up).
3. Run this JavaScript via the chrome javascript_tool to pull every user row with last-seen timestamps:
   ```
   (() => {
     const links = Array.from(document.querySelectorAll('a[href*="/system/users/edit/"]'));
     const seen = new Set();
     const rows = [];
     links.forEach(l => {
       const m = l.getAttribute('href').match(/\/system\/users\/edit\/(\d+)\/general/);
       if (!m || seen.has(m[1])) return;
       seen.add(m[1]);
       const row = l.closest('[role="row"]') || l.closest('tr') || l.parentElement?.parentElement?.parentElement;
       const text = row?.innerText?.replace(/\n/g,' | ');
       rows.push({id: m[1], text});
     });
     return JSON.stringify(rows);
   })()
   ```
4. For each row, parse the Last Seen value. It appears as either "Online", "Away", or a date/time like "04/02/2026 04:31:50 PM". Treat "Online" and "Away" as currently connected (not offline). For any row with a date/time, compute how many hours ago that was vs. the current date/time.
5. Collect every agent whose Last Seen date/time is more than 48 hours in the past. For each one, record: friendly name (or raw name if no friendly name), store/path, last computer, and last-seen timestamp.
6. Compose a concise Claude notification summary:
   - If zero offline agents: "Controlio check: all agents online within 48hrs."
   - If 1+ offline: "Controlio: N agent(s) offline >48hrs:" followed by a bulleted list with name, store, last computer, and last seen.
7. Output the summary as the final message of the run so it appears in Joshua's notification.

Success criteria: A clear report is generated every run, naming any offline agents and their last-seen times, or confirming all are current.

Constraints:
- Do not modify any Controlio settings, rename users, or delete anything.
- Do not attempt credential entry if logged out — report and stop.
- Use Chrome MCP, not computer-use, for the browser interaction.
- Keep the notification short (under 200 words).