---
name: vp-dashboard-refresh
description: Nightly refresh of the Valley Pawn enterprise dashboard (vp-dashboard.pages.dev) — re-parse Slack reports, re-sync artifacts, redeploy to Cloudflare Pages
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
Refresh and redeploy the Valley Pawn enterprise dashboard. The complete runbook is at:
/Users/joshuadavis/Documents/Claude/Projects/Business Dashboard Website/REFRESH_RUNBOOK.md

READ THE RUNBOOK FIRST and follow it exactly. Summary of the steps it defines:

1. UPDATE KPI DATA — Read the latest standard-format report ("Sent using Claude") from each Slack channel and update /Users/joshuadavis/Documents/Claude/Projects/Business Dashboard Website/site/data/kpis.json, preserving the exact JSON schema:
   WEEKLY/MONTHLY FEEDS:
   - #loan-review (C0B08RS2BMK): pastDue rows [store, items, dollars, pct], pastDueTotal, companyLoanBalance, dates.loans
   - #layaway-review (C04N24STDP1): layaway rows, layawayTotal, dates.layaway
   - #company-performance (C0B26GD8D2R): watch[] items
   DAILY FEEDS:
   - #daily-funds-reconcilation (C0B3R9B3S8H): funds {status, expected, actual, note}, dates.funds
   - #items-to-price (C0BA5U0GENL): daily.itemsToPrice {date, stores [[store, items, cost]], total {items, cost}}
   - #pawn-walks (C0B8WR95N31) "Intake Margin" posts: daily.intakeMargin {date, note, stores [[store, items, avgMargin, flags]], company {items, avgMargin, flags}}
   - #chekkit-unanswerd-summary (C0B1PEW0C30): daily.chekkit {date, totalUnanswered, summary}
   DO NOT touch the "bravoDaily" section — it is owned by the daily-bravo-kpis task; preserve whatever is there.
   Update asOf to today. Update feeds[] Last Run column. If a channel has no newer report, keep existing values. NEVER fabricate numbers; on parse failure keep old data.

2. SYNC ARTIFACTS — via the osascript tool run:
   cp -R /Users/joshuadavis/Documents/Claude/Artifacts/* '/Users/joshuadavis/Documents/Claude/Projects/Business Dashboard Website/site/artifacts/' && rm -rf '/Users/joshuadavis/Documents/Claude/Projects/Business Dashboard Website/site/artifacts'/*/versions
   If new artifact folders appeared, add entries to site/data/artifacts.json (standalone=true only if its index.html contains no "window.cowork" references). Update "updated" dates for changed artifacts.

3. DEPLOY — in the sandbox shell, from the mounted Business Dashboard Website folder:
   export CLOUDFLARE_API_TOKEN=$(cat .cloudflare/api_token); export CLOUDFLARE_ACCOUNT_ID=$(cat .cloudflare/account_id); npm install -g wrangler --silent; npx wrangler pages deploy site --project-name=vp-dashboard --commit-dirty=true
   NEVER delete site/_worker.js — it is the password gate.

4. VERIFY — curl https://vp-dashboard.pages.dev/ must return 401 without auth, and 200 with basic auth user "valleypawn" and the password from .cloudflare/site_password. Also verify data/kpis.json parses as valid JSON.

5. Only if a step FAILED, post a one-line failure summary to Slack #general. On success, no Slack post.

<!-- migrated to working model 2026-06-15 -->