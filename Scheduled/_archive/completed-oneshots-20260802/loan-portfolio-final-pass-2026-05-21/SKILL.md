---
name: loan-portfolio-final-pass-2026-05-21
description: DISABLED — superseded by comprehensive analytics spec; will not run.
model: claude-sonnet-5
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

FINAL analysis pass for the Optimize Loan Portfolio project after monthly-sliced pipeline trigger completes.

STEPS:
1. Read STATUS.md at /Users/joshuadavis/Documents/Claude/Projects/Optimize Loan Portfolio/STATUS.md first to confirm context.

2. Check pipeline status: read /Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/results/loan-portfolio-2026-monthly-12mo-2026-05-21T09-30-00.result.json via osascript. Confirm all 62 cells finished (or at least most succeeded). If still in flight, wait/poll for up to 60 more min.

3. Run the v2 analysis:
   osascript: python3 '/Users/joshuadavis/Library/Application Support/Claude/local-agent-mode-sessions/823f6874-6252-4031-ae4e-a3c22d37598e/f6b75d02-cca9-4943-ad6e-88390a3f201d/local_7d4c218c-06bf-4a4e-8925-62088f81f954/outputs/v2_real_analysis.py'

4. Run the decision-doc generator (uses workspace bash — node has docx installed at /sessions/jolly-wizardly-johnson/mnt/outputs/node_modules):
   workspace bash: cd /sessions/jolly-wizardly-johnson/mnt/outputs && node build_v2_decision_docx.js

5. Verify outputs exist in /Users/joshuadavis/Documents/Claude/Projects/Optimize Loan Portfolio/:
   - Loan_Portfolio_Analysis_v2_<date>.xlsx
   - Loan_Portfolio_DecisionDoc_<date>.docx
   - loan_portfolio_v2_summary.json
   - loan_portfolio_dashboard_v2.html (already exists, reads JSON dynamically)

6. Update STATUS.md with the final-pass results: total tickets loaded, cells succeeded, cells failed, headline ROI findings.

7. DM Joshua at U03BB52MDSA on Slack with a short summary: top 3 categories to lend confidently on, top 3 to tighten/stop, per-store ROI ranking, and a link to the Excel/Word/dashboard. Format as markdown.

If the pipeline is incomplete or some cells errored, still run the analysis on partial data and note in the Slack post which stores have incomplete coverage.