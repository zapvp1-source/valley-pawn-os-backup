---
name: monthly-amazon-store-allocation
description: 6th of each month 9 AM — pull prior month's Amazon Business Shipments report by ship-to address, allocate spend to the 5 stores + Corporate, save an xlsx to the Quickbooks Set UP folder, and DM Joshua the per-store/Corporate breakdown for QBO classification.
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
Monthly Amazon "Store Supplies" per-store allocation for Valley Pawn. Runs on the 6th for the PRIOR calendar month. Goal: produce the per-store + Corporate split of Amazon Business spend (by ship-to address) so it can be classified in QuickBooks, then DM Joshua the numbers and save a workbook.

CONTEXT / WHY: Amazon charges hit QBO as a single "Store Supplies" account with no store split. Store-level P&Ls need Amazon supplies allocated per store. The ONLY reliable store key is the ship-to address on each shipment (ZIP → store). Anything not shipped to a store = Corporate. This task reproduces the manual pull that built `2025-Amazon-Store-Allocation.xlsx`.

DO NOT post to Slack on failure — stay silent and just record what failed. Only DM Joshua on success.

### STEP 1 — Compute the target month
- Today is the 6th. Target = the PRIOR calendar month. Compute fromDate = first day of prior month, toDate = last day of prior month. Note: in the Amazon API the month field is **0-indexed** (Jan=0 … Dec=11).
- Example: if today is 2026-07-06, target = June 2026 → fromDate {year:2026,month:5,day:1}, toDate {year:2026,month:5,day:30}.

### STEP 2 — Open the Shipments report
- Use Claude-in-Chrome. Create a tab, navigate to `https://www.amazon.com/b2b/aba/reports?reportType=items_report_2&dateSpanSelection=MONTH_TO_DATE`.
- If the page shows you are NOT logged in to Amazon Business, do NOT attempt to log in — DM Joshua "⚠️ Amazon Business session expired — monthly Amazon allocation could not run. Please log in." and stop.
- Make sure the "Shipping Address" column is included (it is by default in the data). You do not need the UI date picker — you will query the data API directly.

### STEP 3 — Capture and replay the data API (proven method)
The report's table loads from a POST to `…/b2b/aba/ajax/v2/report/rollupTable?...`. Capture one real request (with its auth headers + body), then replay it with your target date range.

1. With `javascript_tool`, install a fetch hook BEFORE triggering a load:
```
window.__cap=[]; if(!window.__origFetch){window.__origFetch=window.fetch;}
window.fetch=function(...a){try{const u=(typeof a[0]==='string')?a[0]:(a[0]&&a[0].url);if(u&&u.includes('/b2b/aba/ajax')){window.__cap.push({url:u,method:(a[1]||{}).method,body:(a[1]||{}).body,headers:(a[1]||{}).headers});}}catch(e){} return window.__origFetch.apply(this,a);}; 'hooked'
```
2. Trigger a request: click the report's "Next page" control (bottom-right) and/or "Generate report". Then confirm `window.__cap` contains a `rollupTable` entry. (Note: returning fetch-derived objects directly can be blocked — store results on `window.*` and read them back in a separate `javascript_tool` call with a short summary string.)
3. Replay with your target dates, large page size, paginating until fewer than pageSize rows come back. Rows nest as `rollupTableView[i].shipments["0..n"].content` (a single row can have multiple sub-shipments). Pull these fields from each shipment's content: `shipZip`, `shipCity`, `shipItemsNetTotal` (use `.rawContent.amount`; fall back to parsing `.content` "$x"). Get `ordDate` from `rollupTableView[i].mandatory["0"].content.ordDate.content`.
```
// inside an async IIFE, for each page:
body=JSON.parse(cap.body); body.dateSpanSelection='CUSTOM_RANGE';
body.fromDate={year:Y,month:M0,day:1}; body.toDate={year:Y,month:M0,day:LASTDAY};
body.pageMarker=marker; body.pageSize=5000;
r=await window.__origFetch(cap.url.replace('MONTH_TO_DATE','CUSTOM_RANGE'),{method:'POST',headers:cap.headers,body:JSON.stringify(body),credentials:'include'});
```
Accumulate all shipment rows into `window.__allrows` = [{date, zip, city, net}]. Read back a summary string to confirm row count + total $.

### STEP 4 — Bucket by ZIP → store / Corporate
Store ZIPs: **22701→Culpeper, 22980→Waynesboro, 22801→Harrisonburg, 24450→Lexington, 24017→Roanoke**. Every other ZIP (incl. Joshua's St Augustine 32095/32092, Palm Coast 32137, Verona 24482, Fishersville 22939, and any other) → **Corporate**. Sum `net` per bucket. Result = 6 numbers: 5 stores + Corporate, plus a grand total and shipment counts.

### STEP 5 — Save a workbook
- Build an xlsx with openpyxl: a Summary tab (Bucket, QBO Class [store name or "Corporate"], Spend, % of total, total row) and a Location Detail tab (every ZIP/city with count + $ and its bucket). Use `$#,##0.00` money format, professional fonts, formulas for totals.
- Save to the Valley Pawn Bookkeeping Google Drive folder if reachable, otherwise to `/Users/joshuadavis/Documents/Claude/Projects/Quickbooks Set UP/` (or the session output folder). Name it `Amazon-Store-Allocation-{YYYY-MM}.xlsx` for the target month. Recalculate formulas if a recalc script is available; ensure zero formula errors.

### STEP 6 — DM Joshua the breakdown (this is the success signal)
DM Joshua (Slack user **U03BB52MDSA**) — only on success:
```
:package: *Amazon Store-Supply Allocation — {Month YYYY}*
By ship-to address. Classify in QBO Store Supplies by class:
• Culpeper — ${...}
• Waynesboro — ${...}
• Harrisonburg — ${...}
• Lexington — ${...}
• Roanoke — ${...}
• *Corporate (non-store)* — ${...}
Total: ${grand} · {N} shipments
Workbook: {path/Drive link}
```
Keep it to these lines. Do not post elsewhere.

### NOTES
- This is read-only in Amazon (a reporting pull) — never place orders or change settings.
- The Amazon net total includes tax and is by order date; it will run a bit higher than the card charges posted that month (timing + tax + the 2nd card 2003). That's expected — these are allocation proportions for the Store Supplies line, not a bank reconciliation.
- Going forward, orders also carry an optional "Location" store tag set at checkout; ship-to address remains the authoritative key this task uses.