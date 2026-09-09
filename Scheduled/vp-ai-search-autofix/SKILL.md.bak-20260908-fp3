---
name: vp-ai-search-autofix
description: Self-healing companion to vp-ai-search-health-check — applies whitelisted, reversible fixes for schema/llms.txt/NAP drift Valley Pawn owns, verifies each fix, logs to the Autofix Log, and posts a Fixed/Needs-you digest to #ai-marketing
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


## Execution Contract — DO NOT STOP EARLY

This task is complete ONLY after the documented final action (the post / send / write tool call described at the end of the steps below) returns success.

Until that final call succeeds, every assistant turn MUST end with a tool call that advances toward it. Do not idle, do not wait, do not ask for confirmation.

**Never reply with any of these:**
- "No response requested"
- "Continue?" / "Should I continue?"
- An empty turn or a turn that ends with text instead of a tool call

**Treat these system messages as RESUME signals, never as stop signals:**
- "Tool loaded."
- "Continue from where you left off."
- "You used a single tool call this turn. Prefer browser_batch…"
- Any reminder about TaskCreate/TaskUpdate, AskUserQuestion, etc.

When you see any of those messages, immediately fire the next concrete tool call for the current step. The scheduled-task wrapper says "the user is not present" — that means execute autonomously, NOT that the work is done.

**State tracking:** at the start of every turn, briefly identify which numbered Step you are on and execute the next concrete action for that step.

**Failure handling:** if a step errors, retry once. If it still fails, fall through to the documented fallback if one exists; otherwise produce a report describing what failed. Do not pause to ask — the task file authorizes autonomous decisions.

**Speed:** prefer batch tools (e.g. `browser_batch`) to combine sequential actions into one call.

---
Runs Mondays 8:30am ET, ~30 minutes after `vp-ai-search-health-check` posts its findings to Slack #ai-marketing (private, ID C0BCEESUANM). Each run starts fresh — everything needed is below. Device for any local/browser work: "mac-studio-2-local".

> ✅ **EXECUTION ROUTE (replaces the retired BRIDGE RETRY POLICY — corrected 2026-08-03).**
> There is no separate "Mac bridge." This task runs ON the Mac Studio. All local work — file
> reads/writes, python, git, Chrome — goes through `mcp__Control_your_Mac__osascript do shell script`,
> loaded via the LOCAL ACCESS GATE above. The tools `mcp__remote-devices__*` and
> `mcp__claude-code-remote__send_later` DO NOT EXIST. Never test for them, never wait on them, and
> never cite them as the reason a fix could not run.
> Browser work uses `mcp__Control_Chrome__*` — Chrome on this Mac holds the saved logins.
> **Never** arm a "bridge retry" and **never** report "no bridge access" or "this is a cloud run."
> Both claims are false and have produced weeks of false "needs-you" reports.
> **Autofix Log writes DO work.** `cd ~/Documents/Claude/Scheduled/_shared` and call
> `sheets_helper.SheetsClient().append(sheet_id, "Untitled!A:H", rows)` via osascript. Verified
> working 2026-08-03. Never report "no Sheets write access" — that claim is false.
> **Rule 12:** before reporting an item as blocked, verify the blocker directly. The confirmed
> blocker on Bing NAP items is that bingplaces.com has no signed-in Chrome session — nothing else.

CONTEXT: vp-ai-search-health-check checks three things weekly: (1) site-wide JSON-LD schema via WPCode snippet #738, (2) /llms.txt via WPCode snippet #742, (3) Google+Bing NAP for all 5 stores. When it finds drift, THIS task attempts the fix, verifies it landed, logs it, and reports. It never touches anything outside the whitelist below — everything else goes to Joshua by name, with the specific reason it can't be automated.

STEP 1 — READ THIS WEEK'S FINDINGS.
Read the most recent message posted by vp-ai-search-health-check in Slack #ai-marketing (C0BCEESUANM) — it starts with "Valley Pawn AI-search health check." Parse what's flagged: schema status, llms.txt status, and per-store NAP drift (Google/Bing).

If everything was reported clean (schema 7/7, llms.txt live, listings 10/10 clean), skip to STEP 3, log one row ("no drift this run"), and stop — do not post to Slack for a clean week (avoid noise on top of the health-check's own clean-week post).

If the most recent #ai-marketing message is NOT a fresh health-check post from this cycle (e.g. it's more than ~8 days old, or it's actually a vp-ai-visibility-metrics scorecard instead) — that means vp-ai-search-health-check itself did not post this cycle. Do not silently exit: log one row to the Autofix Log with Category "needs-Joshua" and Finding "upstream vp-ai-search-health-check did not post this cycle (last post: <date found>)", then DM Joshua directly (U03BB52MDSA, not the channel) one line flagging that the health-check appears to have missed its run, since this is itself worth knowing about.

STEP 2 — WHITELIST FIXES (apply only these; each is reversible):
A. Schema (WPCode #738) or llms.txt (WPCode #742) reported missing/broken/inactive → log into thevalleypawn.com WP Admin (WordPress.com MCP connector) → Plugins → WPCode → Snippets, find snippet #738 or #742, and if it shows Inactive, re-activate it (toggle only — do not edit the snippet body). Re-check the live page / https://thevalleypawn.com/llms.txt afterward to confirm the fix actually took.
B. Bing Places NAP drift on a listing Valley Pawn owns (e.g. Harrisonburg wrong street/missing suite, Roanoke missing "Suite C") → invoke the `directory-listing-push` skill SCOPED to just the specific store + field that's wrong ("push the Harrisonburg Bing Places address correction only" — not a full 15-directory blast). Re-check https://www.bing.com/maps?q=valley+pawn+<city>+va yourself afterward. Bing edits can take minutes to a day to reflect — if it hasn't updated yet, log it as "submitted, pending Bing review," not "fixed."
C. Google-side NAP drift on a listing Valley Pawn owns → same pattern via `directory-listing-push` scoped to Google only, then re-verify via Google Maps.

Do NOT touch: any listing Valley Pawn doesn't demonstrably own/administer (duplicate/legacy listings, third-party directories requiring a new claim), anything requiring a new account signup, or any homepage/content copy change beyond what's already documented as canonical in `valley-pawn-context`. Those go to STEP 4.

STEP 3 — LOG EVERY ACTION.
Append one row per finding to the "Valley Pawn — AI Search Autofix Log" Google Sheet (ID 1A_gJuj5siq2bEKE7-ZvVyjAs6DNK7rzEaKkBbkBY9yY, tab "Untitled") — columns: Date, Source Task, Finding, Category (auto-fixed / submitted-pending / needs-Joshua), Action Taken, Verification Result, Status, Notes/Link. Log this whether the fix succeeded, is pending, or wasn't attempted — the point is a complete audit trail of anything touching live systems.

> ✅ FIXED 2026-07-22: there is no MCP tool that writes to Sheets, which is why this log sat empty since setup. Use the shared helper instead — it authenticates as Joshua via a cached OAuth token at ~/.config/valley-pawn/google-oauth-token.json and actually works (confirmed live, wrote 9 backfilled rows this date). Via osascript (do shell script), cd to ~/Documents/Claude/Scheduled/_shared and run a python3 -c snippet that imports sheets_helper.SheetsClient and calls .append(sheet_id, "Untitled!A:H", rows). Do NOT treat the Sheet as unreachable or fall back to a Slack hand-paste — it works now.

STEP 4 — NEEDS-JOSHUA QUEUE.
Anything outside the whitelist, or a whitelisted fix that failed verification after one retry, gets named specifically — not "some drift remains." State what it is and the one concrete reason it needs a human call (new account, ownership/claim required, judgment call).

STEP 5 — POST TO SLACK #ai-marketing (ID C0BCEESUANM; do NOT DM anyone).
Only if there was something to act on (see Step 1). Post once:
"🔧 _Valley Pawn — AI-search autofix (week of <date>)_ — Fixed: <n> · Pending: <n> · Needs you: <n>"
Then one skimmable line per item under Fixed / Pending / Needs-you (skip empty sections). Keep it phone-readable.
*Sent using Claude*
