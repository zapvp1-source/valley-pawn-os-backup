---
name: vp-ai-visibility-autofix
description: Self-healing companion to vp-ai-visibility-metrics — repairs the GA4 AI-referral channel definition, removes Valley Pawn-owned legacy "Dixie Pawn" content, defaults the Copilot scorecard cell to a working proxy, logs every action, and posts a Fixed/Needs-you digest to #ai-marketing
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


Runs Fridays 9:30am ET, ~30 minutes after `vp-ai-visibility-metrics` posts its scorecard to Slack #ai-marketing (private, ID C0BCEESUANM). Each run starts fresh. Device for any local/browser work: "mac-studio-2-local".

> 🔁 **BRIDGE RETRY POLICY (added 2026-07-22 — fixes the re-reported-drift failure mode).**
> The fixes this task exists for mostly REQUIRE the Mac bridge (mcp__remote-devices__* tools) for
> browser work. At fire time, test the bridge (e.g. a Filesystem read of this file). If UNREACHABLE:
> do NOT run a report-only pass — arm a retry via mcp__claude-code-remote__send_later 2 hours out
> ("BRIDGE RETRY <N>/3", max 3). Only after the 3rd failed retry do a report-only pass, noting
> plainly the Mac was offline all day. When the bridge IS reachable, do the actual fixes. For the
> Autofix Log: if no Sheets write API is available, append rows by opening the sheet in the Mac's
> Chrome via the remote-devices Chrome tools — hand-paste rows in Slack are a last resort only
> when the bridge is down.

CONTEXT: vp-ai-visibility-metrics tests Valley Pawn against a named local rival on 5 AI engines, pulls GA4 AI-referral traffic, and lists "Fix" items. THIS task acts on the parts that are safely, reversibly fixable by Claude alone. Everything else is named for Joshua, with why.

STEP 1 — READ THIS WEEK'S SCORECARD.
Read the most recent "Valley Pawn — AI Visibility Scorecard" message in Slack #ai-marketing (C0BCEESUANM). Note the Fix list and whether Copilot shows "n/t (blocked)".

STEP 2 — WHITELIST FIXES:
A. GA4 "AI Assistants Tracking" channel group not catching an AI source (e.g. chatgpt.com landing in Unassigned/Direct instead of "AI Assistants") → open GA4 Admin (https://analytics.google.com/analytics/web/?authuser=1, account a256872788 / property p353209303, fullcirclepawn@gmail.com) via Claude in Chrome → Admin > Channel Groups > "AI Assistants Tracking" → confirm/repair the Source regex so it matches chatgpt\.com|chat\.openai\.com|openai|perplexity|gemini|copilot|claude\.ai|bard|you\.com|edgeservices (add any missing token — never remove existing ones) → save. Log as "pending verification" this run; confirm it held on next Friday's traffic pull.
B. Legacy "Dixie Pawn" brand name found in content Valley Pawn owns and controls directly (an old company Facebook post, a WordPress page/post) → locate it (Facebook: search the relevant store Page's own posts via the Graph API token from the `facebook-post` skill; WordPress: WordPress.com MCP connector) and edit/delete it so it reads "Valley Pawn." Do NOT touch a customer-authored review's text — you cannot and should not edit someone else's review; if "Dixie Pawn" appears inside a customer review, log it under STEP 3 as "reply, don't edit" and note it in the Needs-you queue only if it needs a brand-voice reply Joshua should see first.
C. Copilot cell shows "n/t (blocked)" because copilot.microsoft.com requires a new personal Microsoft account signup → do NOT create the account — personal identity signup is Joshua's call, not a system fix. Instead substitute Bing's local pack (https://www.bing.com/search?q=<query>) as the Copilot-engine proxy for this and future runs, score presence/rank there the same way the other engines are scored, and label the column "Copilot (via Bing proxy)" in both the Slack post and the Tracker sheet row so nobody mistakes it for true Copilot testing.

Do NOT touch: duplicate/legacy third-party listings (e.g. a "Gold-N-Pawn" ghost listing at the wrong Roanoke address, MapQuest's separate "Dixie Pawn Inc." entry) — claiming/merging those requires a business-verification step Valley Pawn hasn't completed; review-volume gaps — these need real customer reviews, not an edit, so surface as a suggestion to route through the existing Chekkit review-request flow rather than building a new mechanism.

STEP 3 — LOG EVERY ACTION.
Append rows to the "Valley Pawn — AI Search Autofix Log" sheet (ID 1A_gJuj5siq2bEKE7-ZvVyjAs6DNK7rzEaKkBbkBY9yY, tab "Untitled") — same columns as vp-ai-search-autofix. If you changed how a metric is measured (e.g. the Copilot-via-Bing substitution), also note that in this week's row of the AI Visibility Tracker sheet (ID 17gkCl9BpB8yAQZcCs6cg8SDXQfaSGdyKceNJKfwMRMs) so the trend line stays interpretable.

> ✅ FIXED 2026-07-22: there is no MCP tool that writes to Sheets, which is why this log sat empty since setup. Use the shared helper instead — it authenticates as Joshua via a cached OAuth token at ~/.config/valley-pawn/google-oauth-token.json and actually works (confirmed live, wrote 9 backfilled rows this date). Via osascript (do shell script), cd to ~/Documents/Claude/Scheduled/_shared and run a python3 -c snippet that imports sheets_helper.SheetsClient and calls .append(sheet_id, "Untitled!A:H", rows) for the Autofix Log, or .update()/.append() on the Tracker sheet for the Copilot-proxy note. Do NOT treat either sheet as unreachable or fall back to a Slack hand-paste — it works now.

STEP 4 — NEEDS-JOSHUA QUEUE.
Name each non-automatable item specifically with the one concrete reason (ownership/claim, needs a real review, needs his decision).

STEP 5 — POST TO SLACK #ai-marketing (ID C0BCEESUANM; do NOT DM anyone).
Always post, regardless of outcome:
"🔧 _Valley Pawn — AI-visibility autofix (week of <date>)_ — Fixed: <n> · Needs you: <n>"
One skimmable line per item under each heading (skip empty sections).
*Sent using Claude*
