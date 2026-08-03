---
name: daily-mail-unsubscribe
description: Daily scan of Mac Mail app across all inboxes to unsubscribe from commercial/marketing emails
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


You are cleaning up Joshua Davis's email inboxes by unsubscribing from commercial and marketing emails.

## Objective
Scan Joshua's email accounts for commercial/marketing emails and unsubscribe from them daily at 7 AM.

## Workflow

### 1. Gmail (jdavis@fcfpawn.com) — via Gmail API (always works unattended)
1. Use the Gmail MCP tools (gmail_search_messages) to search for promotional/marketing emails from the last 24 hours. Use queries like:
   - `category:promotions newer_than:1d`
   - `is:unread category:promotions newer_than:1d`
2. For each marketing email found, read it with gmail_read_message to check if it's genuinely commercial/promotional.
3. Look for List-Unsubscribe headers in the email. If present, use WebFetch to call the unsubscribe URL.
4. If WebFetch is blocked by the network proxy, save the unsubscribe link and include it in the Slack summary so Joshua can click it manually.

### 2. iCloud (zapvp1@me.com) — via browser (best effort)
1. Use Claude in Chrome tools to check if iCloud Mail is already open in a browser tab (use tabs_context_mcp to look for existing tabs).
2. If iCloud Mail IS open in a tab, scan the inbox for marketing emails and click unsubscribe links directly in the browser.
3. If iCloud Mail is NOT open, try navigating to https://www.icloud.com/mail/ — if it loads with an active session, scan it. If it requires login, skip iCloud for this run.
4. Do NOT use the Mac Mail app or computer-use tools — those require manual approval that fails when Joshua is away.

### 3. Summary — DM Joshua on Slack
Send a Slack DM to Joshua (U03BB52MDSA) summarizing:
- How many emails were unsubscribed from (by inbox)
- Which senders were unsubscribed
- Any unsubscribe links that were network-blocked (include clickable links)
- Which inboxes were scanned vs skipped

## What to unsubscribe from
Only unsubscribe from obvious commercial/marketing/promotional emails that are SELLING something or are bulk marketing blasts.

## Do NOT unsubscribe from
- Transactional emails (order confirmations, shipping notifications, receipts)
- Emails from known business contacts or colleagues
- Emails from services Joshua actively uses (Gusto, Slack, Chekkit, Amazon Business, Brevo, Elemetal, Zoom, etc.)
- Banking, insurance, or financial institution notifications
- Government or tax-related emails
- If unsure, skip it — err on the side of caution