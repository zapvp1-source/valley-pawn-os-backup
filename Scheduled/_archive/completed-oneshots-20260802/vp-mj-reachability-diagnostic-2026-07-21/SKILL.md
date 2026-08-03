---
name: vp-mj-reachability-diagnostic-2026-07-21
description: One-time diagnostic: determine exactly why Midjourney has been reported "unreachable" in scheduled vp-content-batch runs when it's reachable in interactive sessions — is it a Chrome/computer-use permission gap in cold scheduled-task sessions, a login/session issue, or a real MJ outage?
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


This is a one-time diagnostic run, not a content-generation run. Do not generate any real hero images or publish anything. Your only job is to determine, definitively, why Midjourney has been reported as "unreachable" in recent scheduled `vp-content-batch-weekly` runs (2026-07-20 fell back to Canva for all 13 heroes citing "Midjourney unreachable this session") even though it was confirmed reachable and logged in (as valley_pawn) when checked interactively in a live Claude conversation on 2026-07-21 around 12 PM ET.

Steps:
1. Attempt to use Chrome/computer-use tools to navigate to `https://www.midjourney.com/imagine`, exactly as `vp-hero-image` Step 6 describes. Note precisely what happens:
   - Does a permission/access-request prompt block the navigation (i.e., does this cold scheduled-task session start without Chrome/computer-use access pre-approved, requiring a human to click "Allow" that isn't there)? This is the leading hypothesis — scheduled tasks may need their tool approvals granted once via an interactive "Run now" before they persist for future cron firings.
   - If Chrome access works fine, does the page load logged-in, logged-out, or show a "fast hours exhausted" / rate-limit / paywall banner?
   - If logged out, is it a session-expiry issue (Google saved password autofill didn't fire) or something else?
2. Report EXACTLY what you observed — the literal error/state, not a guess. If you hit a permission wall, quote the exact message. If the page loaded fine, describe what's on it (logged in as who, any credit/plan indicators, any banners).
3. Do NOT fall back to Canva, do NOT generate anything, do NOT publish anything. This is diagnosis only.
4. Write your findings to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn Studios/output/2026-07-21/mj_reachability_diagnostic.json` with fields: `chrome_access_granted` (bool), `permission_prompt_seen` (bool + exact text if yes), `page_loaded` (bool), `logged_in_as` (string or null), `fast_hours_status` (string or null), `conclusion` (one of: "permission_gap", "session_expired", "mj_outage", "reachable_no_issue", "other"), `raw_notes` (string).
5. DM Joshua a short, concrete summary: what exactly is blocking MJ in scheduled runs (not "it was unreachable" — the actual mechanical reason), and whether it's something that fixes itself now vs. something that needs a one-time action from him (e.g., approving Chrome access for this task, or re-logging into MJ).

This diagnostic matters because Joshua has said pushing a Canva fallback and just reporting "MJ didn't respond" isn't good enough — he wants the actual blocking mechanism identified and fixed so future scheduled batches reliably reach MJ.